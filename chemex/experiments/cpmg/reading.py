"""Read the experimental CPMG data."""
import importlib

import numpy as np


def read_profiles(path, filenames, details, model):
    """Read the CPMG profiles."""
    experiment_type = details["type"].split(".")

    details["name"] = name_experiment(details)

    experiment_module = importlib.import_module(
        ".".join(
            ["chemex.experiments", experiment_type[0], "profiles", experiment_type[1]]
        )
    )

    Profile = getattr(experiment_module, "Profile")

    dtype = [("ncycs", "i4"), ("intensities", "f8"), ("errors", "f8")]

    profiles = []

    for profile_name, filename in filenames.items():
        full_path = path / filename
        data = np.loadtxt(full_path, dtype=dtype)
        profiles.append(Profile(profile_name, data, details, model))

    error = details.get("error", "file")

    if error not in {"file", "auto"}:
        print("Warning: The 'error' option should either be 'file' or ")
        print("'auto'. Using the default 'file' option.")
        error = "file"

    if error == "auto":

        noise_values = []

        for profile in profiles:
            noise_values.append(profile.estimate_noise())

        noise_mean = np.mean(noise_values)

        for profile in profiles:
            profile.data["errors"] = noise_mean

    return profiles


def name_experiment(experiment_details=None):
    """Generate a unique name for the experiment."""
    if not experiment_details:
        experiment_details = dict()

    if "name" in experiment_details:
        name = experiment_details["name"].strip().replace(" ", "_")

    else:
        exp_type = experiment_details["type"].replace(".", "_")
        h_larmor_frq = float(experiment_details["h_larmor_frq"])
        temperature = float(experiment_details["temperature"])
        time_t2 = float(experiment_details["time_t2"])

        name = "{:s}_{:.0f}ms_{:.0f}MHz_{:.0f}C".format(
            exp_type, time_t2 * 1e3, h_larmor_frq, temperature
        ).lower()

    return name
