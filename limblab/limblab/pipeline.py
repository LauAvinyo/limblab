import os
import shutil

import typer


def _create_experiment(experiment_folder_path, experiment_name):
    # Construct the full path
    full_path = os.path.join(experiment_folder_path, experiment_name)

    # Check if the path exists and ask for deletion confirmation
    if os.path.exists(full_path):
        typer.echo(f"The directory {full_path} already exists.")
        delete = typer.confirm(
            "Do you want to delete it and create a new one?", default=False)
        if delete:
            shutil.rmtree(full_path)
            os.makedirs(full_path)
            typer.echo(f"Deleted and recreated the directory {full_path}.")
        else:
            typer.echo("Exiting the program.")
            raise typer.Exit()
    else:
        os.makedirs(full_path)
        typer.echo(f"Created the directory {full_path}.")

    # Prompt for limb side
    limb_side = typer.prompt("Enter the limb side (R/L)", default="R")

    # Prompt for limb position
    limb_position = typer.prompt("Enter the limb position (H/F)", default="H")

    # Prompt for volume spacing
    volume_spacing = None
    while True:
        volume_spacing_input = typer.prompt(
            "Enter the volume spacing (three float values separated by space). Click enter for default is (0.65, 0.65, 2). Or type 'q' to quit and comeback later.)",
            default="0.65 0.65 2")
        if volume_spacing_input.lower() == 'q':
            typer.echo("Exiting the program.")
            break
        try:
            volume_spacing = list(map(float, volume_spacing_input.split()))
            if len(volume_spacing) == 3:
                break
            else:
                typer.echo("Please enter exactly three float values.")
        except ValueError:
            typer.echo(
                "Invalid input. Please enter three float values separated by space."
            )

    # Display the collected information
    typer.echo(f"Experiment Name: {experiment_name}")
    typer.echo(f"Experiment Folder Path: {experiment_folder_path}")
    typer.echo(f"Limb Side: {limb_side}")
    typer.echo(f"Limb Position: {limb_position}")
    typer.echo(f"Volume Spacing: {volume_spacing}")

    # Crate the pipeline, and add the data.
    pipeline = os.path.join(full_path, "pipeline.log")
    with open(pipeline, "w", encoding="utf-8") as f:
        print("BASE", full_path, file=f)
        print("SIDE", limb_side, file=f)
        print("POSITION", limb_position, file=f)
        print("SPACING", " ".join((str(i) for i in volume_spacing)), file=f)

    typer.echo(f"✅ Folder and {pipeline} file created!")

    # # If at some moment we want to allow the user to get the staging
    # # Prompt for limb stage
    # limb_stage = typer.prompt(
    #     "Enter the limb stage",
    #     prompt_suffix=" (if not sure, you can stage it later)")
    # typer.echo(f"Limb Stage: {limb_stage}")
