import pyfair

# Create model and calculate.
model1 = pyfair.FairModel(name="Regular Model 1", n_simulations=10_000)
model1.input_data('Loss Event Frequency', low=20, mode=100, high=900)
model1.input_data('Probable Loss Magnitude', low=3_000_000, mode=3_500_000, high=5_000_000)
model1.calculate_all()

# Create another model
model2 = pyfair.FairModel(name="Regular Model 2", n_simulations=10_000)
model2.input_data('Loss Event Frequency', low=.5, mode=.7, high=.9)
model2.input_data('Probable Loss Magnitude', low=2_000_000_000, mode=3_000_000_000, high=5_000_000_000)
model2.calculate_all()

# Load a model from a serialized json file
with open('./serialized_model.json') as f:
    json = f.read()
    model3 = pyfair.FairModel.read_json(json)

# Create metamodel
mm = pyfair.FairMetaModel(name='My Meta Model!', models=[model1, model3])
mm.calculate_all()

# Create and output report.
fsr = pyfair.FairSimpleReport([model3, mm])
fsr.to_html('output.html')
