# Hoxa11 pipeline

In this guide we will analyze an HCR with Hoxa11 expression. 

The raw data can be found here:
We have 1: The DAPI channel and 2. The HCR oh Hoxa11. 

First of all, we want to set up and experiment.

```bash
limb create-experiment Hoxa11
```

This will generate the log file for this experiment. 

Next, we have to clean up the volumes. We will first start with the DAPI, so we can extract the surface and hence, stage and align to a reference limb. 


The rest are done with tools adding the code, where it belongs!

For the figure panel A4 and B4
