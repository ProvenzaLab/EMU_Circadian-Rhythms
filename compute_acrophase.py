import pandas as pd
import numpy as np
import os
from scipy.stats import zscore
from scipy.optimize import curve_fit
from scipy import stats
from tqdm.auto import tqdm
from joblib import Parallel, delayed
import joblib


class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
    def __call__(self, *args, **kwargs):
        tqdm_obj.update(n=self.batch_size)
        return super().__call__(*args, **kwargs)

old_callback = joblib.parallel.BatchCompletionCallBack

def parallel_with_tqdm(n_jobs, total):
    def _run(tasks):
        global tqdm_obj
        tqdm_obj = tqdm(total=total)
        joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
        try:
            return Parallel(n_jobs=n_jobs)(tasks)
        finally:
            joblib.parallel.BatchCompletionCallBack = old_callback
            tqdm_obj.close()
    return _run

def cosinor_factory(omega_hours=24):
    def cosinor(t, M, A, phi):
        omega = 2 * np.pi / omega_hours
        return M + A * np.cos(omega * t + phi)
    return cosinor

def fit_function(func, t, y, M0, A0, phi0, bounds=([-np.inf, 0, -np.pi], [np.inf, np.inf, np.pi]), maxfev=10000):
    """
    Fit a function to the data using curve_fit and return fit parameters and p values.

    Params:
    - func (callable): Function to fit.
    - t (array-like): Time values.
    - y (array-like): Observed values.
    - M0 (float): Initial guess for the mean value.
    - A0 (float): Initial guess for the amplitude.
    - phi0 (float): Initial guess for the phase shift.
    - bounds (tuple): Bounds for the parameters.
    - maxfev (int): Maximum number of function evaluations.

    Returns:
    - M_fit (float): Fitted mean value.
    - A_fit (float): Fitted amplitude.
    - phi_fit (float): Fitted phase shift in radians.
    - p_values (array): P-values for the fitted parameters.
    """

    # Initial guesses: M=mean, A=half range, phi=0
    if M0 is None: M0 = np.mean(y)
    if A0 is None: A0 = (np.max(y) - np.min(y)) / 2
    if phi0 is None: phi0 = 0

    popt, pcov = curve_fit(
        func, t, y,
        p0=[M0, A0, phi0],
        bounds=bounds,
        maxfev=maxfev
    )

    perr = np.sqrt(np.diag(pcov))
    n = len(y)
    p = len(popt)
    dof = max(0, n-p)
    t_stats = popt / perr
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), dof))  # two-tailed p-values

    M_fit, A_fit, phi_fit = popt
    # if A_fit < 0:
    #     A_fit = -A_fit
    #     phi_fit += np.pi
    
    return M_fit, A_fit, phi_fit, p_values

def apply_sliding_cosinor(group_df, cosinor_omega=24, window_size_days=3):
    cosinor = cosinor_factory(cosinor_omega)
    half_window_size = window_size_days // 2

    result = {
        'days_since_dbs': [],
        'left_cosinor_acrophase': [],
        'left_cosinor_amplitude': [],
        'left_cosinor_mean': [],
        'right_cosinor_acrophase': [],
        'right_cosinor_amplitude': [],
        'right_cosinor_mean': []
    }

    for day in np.arange(group_df['days_since_dbs'].min(), group_df['days_since_dbs'].max()+1):
        window_df = group_df.loc[group_df['days_since_dbs'].between(day - half_window_size, day + half_window_size)].copy()
        if len(window_df) < 10:
            continue

        t = window_df['CT_timestamp'].dt.hour + window_df['CT_timestamp'].dt.minute / 60 + window_df['CT_timestamp'].dt.second / 3600
        y_left, y_right = window_df[['lfp_left_OvER_interpolate_z_scored', 'lfp_right_OvER_interpolate_z_scored']].values.T
        mask_left, mask_right = ~np.isnan(y_left), ~np.isnan(y_right)

        t_left, t_right = t[mask_left], t[mask_right]
        y_left, y_right = y_left[mask_left], y_right[mask_right]
        if len(t_left) != 0:
            M_left, A_left, phi_left, p_left = fit_function(cosinor, t_left, y_left, M0=0, A0=1, phi0=0)
            phi_left = (-phi_left) % (2 * np.pi)
            phi_left = phi_left * 24 / (2 * np.pi)
        else:
            M_left, A_left, phi_left, p_left = np.nan, np.nan, np.nan, np.nan
        if len(t_right) != 0:
            M_right, A_right, phi_right, p_right = fit_function(cosinor, t_right, y_right, M0=0, A0=1, phi0=0)
            phi_right = (-phi_right) % (2 * np.pi)
            phi_right = phi_right * 24 / (2 * np.pi)
        else:
            M_right, A_right, phi_right, p_right = np.nan, np.nan, np.nan, np.nan

        result['days_since_dbs'].append(day)
        result['left_cosinor_acrophase'].append(phi_left)
        result['left_cosinor_amplitude'].append(A_left)
        result['left_cosinor_mean'].append(M_left)
        result['right_cosinor_acrophase'].append(phi_right)
        result['right_cosinor_amplitude'].append(A_right)
        result['right_cosinor_mean'].append(M_right)

    return pd.DataFrame(result)



def process_one_csv(csv_path):
   
    


    df = pd.read_csv(csv_path, parse_dates=["date"])
    
    chan_name = df["ch"].iloc[0]
    pat_name  = df["sub"].iloc[0]
    ch0 = str(chan_name).strip().upper()
    hemi = ch0[0] if len(ch0) else ""

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")
    # set index 
    df = df.set_index("date")
    # resample to 10 minute intervals, mean power
    df_g = df.groupby("band")["power"].resample("10min").mean().interpolate(method='linear').reset_index()

    df_g["CT_timestamp"] = df_g["date"]

    start_day = df_g["CT_timestamp"].dt.normalize().min()
    df_g["days_since_dbs"] = (
    df_g["CT_timestamp"].dt.normalize() - start_day
    ).dt.days.astype(int)

    results = []  

    for band, g in df_g.groupby("band",sort=False):
        power_z = zscore(g["power"], nan_policy="omit")

        if hemi == "R":
            left_series = np.full(len(power_z), np.nan)
            right_series = power_z
        elif hemi == "L":
            left_series = power_z
            right_series = np.full(len(power_z), np.nan)
        else:
            continue

        df_input = pd.DataFrame({
        "days_since_dbs": g["days_since_dbs"],
        "CT_timestamp": g["CT_timestamp"],
        "lfp_left_OvER_interpolate_z_scored": left_series,
        "lfp_right_OvER_interpolate_z_scored": right_series,  # duplicated hemi
        })

        out = apply_sliding_cosinor(df_input, cosinor_omega=24, window_size_days=3)
        out["band"] = band
        out["chan_name"] = chan_name
        out["patient_name"] = pat_name
        out["hemi"] = hemi if hemi in {"L", "R"} else "no_hemisphere_data"
        results.append(out)
    
    if results:
        return pd.concat(results, ignore_index=True)
    else:
        return pd.DataFrame()   
   
fol = r"Z:\Provenza\EMU_Circadian-Rhythms\chunks_power"

all_results = []


csv_paths = [os.path.join(fol, f) for f in os.listdir(fol)]

if __name__ == "__main__":
    all_dfs = Parallel(n_jobs=29,verbose=10)(delayed(process_one_csv)(p)for p in csv_paths)

    all_results = pd.concat([df for df in all_dfs if not df.empty],ignore_index=True)

    all_results.to_csv(
        r"Z:\Provenza\EMU_Circadian-Rhythms\acrophase\cosinor_results(leftvsrightHemi).csv",
        index=False
        )
