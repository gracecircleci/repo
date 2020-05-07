import unittest
from components.sign_on import SignOn

class SignOnTest(unittest.TestCase):
    def test_check(self):
        # just a simple check of the test framework
        self.assertTrue(True)

    def test_signon(self):
        signonObj = None
        signonObj = SignOn('https', 'api-stage.vizio.com',
                           'api/1.0.1.0/auth/authserversigninwithdetails.aspx',
                           'clientTypeId=2000001&appTypeId=2000001&_url=1')
        status_code, jsonobj = signonObj.sign_in()
        self.assertEqual(status_code, 200)
        self.assertTrue(jsonobj != None)

        status_code, jsonobj2 = signonObj.get_data(jsonobj)
        self.assertEqual(status_code, 200)
        self.assertTrue(jsonobj2 != None)

        status_code, jsonobj3 = signonObj.get_root_nav(jsonobj2)
        self.assertTrue(status_code, 200)
        self.assertTrue(jsonobj3 != None)


if __name__ == '__main__':
    unittest.main()
