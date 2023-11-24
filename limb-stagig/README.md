![](https://user-images.githubusercontent.com/32848391/108870607-8d6cf780-75f8-11eb-889a-5fe807939c3d.png)

A pipeline for creating/updating a mouse limb gene expression DB, which includes:
1. limb developmental staging
2. morphing and registering to a predefined timecourse set of shapes
3. mapping and adding gene expression data


# Install

- [optional] Install CERN root v6 by downloading from [here](https://root.cern/install/all_releases)
(check `src/makefile`).
- `pip install -U git+https://github.com/marcomusy/vedo.git`
- `git clone https://github.com/marcomusy/gene_mapper.git`
- `cd gene_mapper`
- [optional] `cd src && make && cd ..` ( change the path to ROOT on `makefile`)


## Usage example

```bash
./gene_mapper.py -i test_image_limb.png
```

Or

```bash
./gene_mapper.py -g SOX9 -i data/sox9/segmented/11-09.png
```

- Can redo the staging interactively
- Automatic left/right detection, no specific orientation needed in drawing the line
- Staging result is stored for later use

Output:

![](https://user-images.githubusercontent.com/32848391/108876247-539eef80-75fe-11eb-9203-9b719295f3f0.png)

- Press m to morph the boundary to match the template timecourse:

![](https://user-images.githubusercontent.com/32848391/108876779-dd4ebd00-75fe-11eb-94c1-59bec565758d.png)

- Press q to map the gene expression to the final mesh:

![](https://user-images.githubusercontent.com/32848391/108876780-dde75380-75fe-11eb-893f-981ad04fcd58.png)


## CLI options

Check out:

`./gene_mapper.py -h`

![](https://user-images.githubusercontent.com/32848391/108874223-3e28c600-75fc-11eb-83a2-2a173529a0eb.png)
