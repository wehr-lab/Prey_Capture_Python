# step1:
# changed for A1suppression first try
# conda activate Lisbet01
# move to d:\Lisbet\datasets
# note that the training CSVs have to each be in a different subdir within d:\Lisbet\datasets\A1suppression

# step1:
# very slow step
betman train_model \
    -v \
    --task_ids=cons,order,shift,warp \
    --data_format=DLC \
    --run_id=combinedLarge02_truncatedCSVs \
    --seed=1234 \
    --epochs=100 \
    --emb_dim=64 \
    --num_layers=8 \
    --num_heads=8 \
    --hidden_dim=256 \
    --train_sample=0.05\ 
    combinedLarge02_truncatedCSVs\