import pyfair

# Create using LEF (PERT), PL, (PERT), and SL (constant)
model1 = pyfair.FairModel(name="Regular Model 1", n_simulations=10_000)
model1.input_data('Loss Event Frequency', low=20, mode=100, high=900)
model1.input_data('Primary Loss', low=3_000_000, mode=3_500_000, high=5_000_000)
model1.input_data('Secondary Loss', constant=3_500_000)
model1.calculate_all()

# Create another model using LEF (Normal) and LM (PERT)
model2 = pyfair.FairModel(name="Regular Model 2", n_simulations=10_000)
model2.input_data('Loss Event Frequency', mean=.3, stdev=.1)
model2.input_data('Loss Magnitude', low=2_000_000_000, mode=3_000_000_000, high=5_000_000_000)
model2.calculate_all()

# Create metamodel by combining 1 and 2
mm = pyfair.FairMetaModel(name='My Meta Model!', models=[model1, model2])
mm.calculate_all()

# Create report comparing 2 vs metamodel.
fsr = pyfair.FairSimpleReport([model1, mm])
fsr.to_html('output.html')
