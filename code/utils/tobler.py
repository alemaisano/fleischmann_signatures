import pandas as pd
import numpy as np


def area_max(source_df, target_df, variables):
    """
    Join attributes from source based on the largest intersection. In case of a tie it picks the first one.
    
    Parameters
    ----------
    source_df : GeoDataFrame
        GeoDataFrame containing source values
    target_df : GeoDataFrame
        GeoDataFrame containing source values
    variables : string or list-like
        column(s) in dataframes for variable(s)
    
    Returns
    -------
    GeoDataFrame
    
    Notes
    -----
    TODO: preserve dtype where possible
    
    """    
    target_df = target_df.copy()
    target_ix, source_ix = source_df.sindex.query_bulk(target_df.geometry, predicate='intersects')
    areas = target_df.geometry.values[target_ix].intersection(source_df.geometry.values[source_ix]).area

    main = []
    for i in range(len(target_df)):
        mask = target_ix == i
        if np.any(mask):
            main.append(source_ix[mask][np.argmax(areas[mask])])
        else:
            main.append(np.nan)
    
    main = np.array(main)
    mask = ~np.isnan(main)
    if pd.api.types.is_list_like(variables):
        for v in variables:
            arr = np.empty(len(main), dtype=object)
            arr[:] = np.nan
            arr[mask] = source_df[v].values[main[mask].astype(int)]
            target_df[v] = arr
    else:
        arr = np.empty(len(main), dtype=object)
        arr[:] = np.nan
        arr[mask] = source_df[variables].values[main[mask].astype(int)]
        target_df[variables] = arr

    return target_df


def area_interpolate(source_df, target_df, extensive_variables):
    """
    Areal-weighted interpolation of extensive variables (e.g. counts such as
    population or jobs) from source polygons onto target polygons.

    Each source polygon's value is distributed across every target polygon it
    intersects, in proportion to the share of the *source* polygon's area
    that falls within that target. Source area not covered by any target
    (e.g. a hectare cell that is mostly street or open space with no
    tessellation cell) is not reallocated elsewhere, matching the behaviour
    of ``tobler.area_weighted.area_interpolate`` for extensive variables.

    Parameters
    ----------
    source_df : GeoDataFrame
        GeoDataFrame containing source values, e.g. a statistical grid.
    target_df : GeoDataFrame
        GeoDataFrame to receive interpolated values, e.g. tessellation cells.
    extensive_variables : string or list-like
        column(s) in source_df holding extensive (sum-preserving) variables.

    Returns
    -------
    GeoDataFrame
        Copy of target_df with one summed column per extensive variable.
    """
    if not pd.api.types.is_list_like(extensive_variables):
        extensive_variables = [extensive_variables]

    target_df = target_df.copy()
    target_ix, source_ix = source_df.sindex.query_bulk(target_df.geometry, predicate='intersects')
    inter_areas = target_df.geometry.values[target_ix].intersection(source_df.geometry.values[source_ix]).area
    source_areas = source_df.geometry.values[source_ix].area
    weights = np.divide(inter_areas, source_areas, out=np.zeros_like(inter_areas), where=source_areas > 0)

    n = len(target_df)
    for v in extensive_variables:
        contributions = source_df[v].values[source_ix] * weights
        totals = np.zeros(n)
        np.add.at(totals, target_ix, contributions)
        target_df[v] = totals

    return target_df