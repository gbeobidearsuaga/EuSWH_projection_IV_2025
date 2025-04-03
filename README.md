# EuSWH_projection_IV_2025
### Scripts for  “Increasing Central and Northern European Summer Heatwave Intensity Due to Forced Internal Variability Changes”
### by Goratz Beobide-Arsuaga (goratz.beobide.arsuaga@uni-hamburg.de)

### Download data from:
- EOBS => Copernicus Climate Data Store (https://cds.climate.copernicus.eu/).
- SMILES => Earth System Grid Federation (ESGF) nodes (https://esgf.llnl.gov/nodes.html).

### Data processing with CDO (scripts in 0_cdo_files). 
- For t2max and mrso: individual files are merged, regridded to MPI-GE grid, and the European domain is selected. 
- For global mean temperatures (GMT): individual tas files are merged and the weighted area average is computed.

### Identifying heatwave days and computing their intensity (the core scripts for identifying heatwaves are located in "core_code"):
1. We compute two sets of t2max anomalies. 
  - "anomaly_t2max" for non-detrended data: compute t2max anomalies to deseasonalize data.
  - "anomaly_t2max_detrended" for detrended data: compute detrended t2max anomalies to deseasonalize data and remove the ensemble mean trend.
2. Compute heatwave threshold: 90th percentile based on a centered 15-day running window and 1985-2014 reference period.
3. Identify heatwave days: t2max exceeding the threshold for at least 6 consecutive days. 
4. Compute cumulative heat.
5. Integrate cumulative heat for summer months (JJA) and European domain.

### Scripts for the regression analysis and figures: "2_analysis_paper".
