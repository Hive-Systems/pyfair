import pyfair

# Create model and calculate.
model1 = pyfair.FairModel(name="Regular Model 1", n_simulations=10_000)
model1.input_data('Loss Event Frequency', low=20, mode=100, high=900)
model1.input_data('Loss Magnitude', low=3_000_000, mode=3_500_000, high=5_000_000)
model1.calculate_all()

# Create another model
model2 = pyfair.FairModel(name="Regular Model 2", n_simulations=10_000)
model2.input_data('Loss Event Frequency', mean=.3, stdev=.1)
model2.input_data('Loss Magnitude', low=2_000_000_000, mode=3_000_000_000, high=5_000_000_000)
model2.calculate_all()

# Create metamodel by combining 1 and 2
mm = pyfair.FairMetaModel(name='My Meta Model!', models=[model1, model2])
mm.calculate_all()

# Create and output report.
fsr = pyfair.FairSimpleReport([model2, mm])
fsr.to_html('output.html')
