
  AI-Pacman ~ Code


  1. Directory Structure

  File/Directory    | Purpose
  ------------------|----------------------------------------------
  pacman_gymenv.py  | OpenAI Gym Wrapper for Pacman
  research.ipynb    | jupyter notebook containing the training and
		    | hyperparamter optimization, as well as analysis
		    | of the results
  visualise_model   | script that takes a model and the corresponding
                    | map. This script will visually run a model
  analysis          | contains plots of the different models
  optuna_studies    | contains the different optuna studies
  pacman            | contains the pacman game
  saved_data        | saved data from the previous setup

  2. Running and building

  No building is needed. There are 3 things you can run.
  1. pacman.py:           play pacman in your terminal
  2. visualise_model:     visualise a model
       `./visualise_model <model> <corresponding map>`

 3. research.ipynb

 The research.ipynb contains 3 main sections. A section related to the
 training of hyperparmters. A section for training the final model. And finally,
 a section related to the analysis of the model.

 4. Data present at the moment

 The data present does not necessarily match the data in the report. There have
 been many benchmarks created and deleted over time. There has also been
 training on many machines. No system was set up to synchronize this data.

