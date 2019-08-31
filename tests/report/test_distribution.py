import unittest




class TestFairBaseReport(unittest.TestCase):



    def setUp(self):
        self._fbr = FairBaseReport()
        self._model_1 = FairModel('model1', n_simulations=5)
        self._model_1.input_data('Risk', mean=100, stdev=5)
        self._model_2 = FairModel('model2', n_simulations=5)
        self._model_2.input_data('Risk', mean=1000, stdev=50)
        self._metamodel = FairMetaModel(
            name='meta', 
            models=[self._model_1, self._model_2],
        )

    def tearDown(self):
        self._fbr = None
        self._model_1 = None
        self._model_2 = None
        self._metamodel = None



if __name__ == '__main__':
    unittest.main()
