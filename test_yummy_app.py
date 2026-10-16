import unittest
from unittest.mock import patch
from yummy_app import YummyApp
import gps_service


# ==============================================================================
# CAP DO 1: Bo test co ban cho san (Moi chi dat ~35% Coverage)
# ==============================================================================
class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang"""

    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)

    @patch.dict("yummy_app.MENU", {"pho_bo_sau_rieng": 999000})
    def test_pho_bo_sau_rieng(self):
        """Kiem tra mon dac biet pho_bo_sau_rieng co gia 999000"""
        cart = {"pho_bo_sau_rieng": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 999000)


# ==============================================================================
# CAP DO 2 (TIET 3): BO TEST NANG CAO DUA TREN THIET KE MA TRAN TEST CASE
# ==============================================================================
class TestMediumLevel(unittest.TestCase):
    """Kiem thu chuc nang ap dung ma khuyen mai (4 kich ban + ngoai le)"""

    def test_apply_promo_code_valid_online(self):
        """Kich ban 1: Online hop le giam 10%"""
        app = YummyApp(network_status="online", os_version=15)
        total = 100000.0
        self.assertAlmostEqual(app.apply_promo_code(total, "GIAM10"), 90000.0)

    def test_apply_promo_code_offline_raises_connection_error(self):
        """Kich ban 2: Offline nem ConnectionError"""
        app = YummyApp(network_status="offline", os_version=15)
        with self.assertRaises(ConnectionError):
            app.apply_promo_code(100000.0, "GIAM10")

    def test_apply_promo_code_new_os_valid(self):
        """Kich ban 3: Ma dac biet tren OS 15 hop le giam 20%"""
        app = YummyApp(network_status="online", os_version=15)
        total = 100000.0
        self.assertAlmostEqual(app.apply_promo_code(total, "NEW_OS_ONLY"), 80000.0)

    def test_apply_promo_code_new_os_lower_version_raises_value_error(self):
        """Kich ban 4: Ma dac biet tren OS 14 (<15) nem ValueError"""
        app = YummyApp(network_status="online", os_version=14)
        with self.assertRaises(ValueError):
            app.apply_promo_code(100000.0, "NEW_OS_ONLY")

    def test_apply_promo_code_invalid_code_raises_value_error(self):
        """Kich ban bo sung: Ma khuyen mai khong ton tai nem ValueError"""
        app = YummyApp(network_status="online", os_version=15)
        with self.assertRaises(ValueError):
            app.apply_promo_code(100000.0, "MA_KHONG_TON_TAI")


class TestHardLevel(unittest.TestCase):
    """Kiem thu chuc nang de xuat nha hang lan can su dung Mocking GPS"""

    def setUp(self):
        self.app = YummyApp()

    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_in_range(self, mock_gps):
        """Kich ban 1: Mock GPS trong vung (10.0, 105.0)"""
        mock_gps.return_value = (10.0, 105.0)
        restaurants = self.app.get_nearby_restaurants()
        self.assertEqual(restaurants, ["Nha hang Pho Ly Quoc Su", "Bun cha Huong Lien"])
        mock_gps.assert_called_once()

    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_out_of_range(self, mock_gps):
        """Kich ban 2: Mock GPS ngoai vung (20.0, 110.0) tra ve danh sach rong"""
        mock_gps.return_value = (20.0, 110.0)
        restaurants = self.app.get_nearby_restaurants()
        self.assertEqual(restaurants, [])
        mock_gps.assert_called_once()

    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_gps_signal_lost(self, mock_gps):
        """Kich ban 3: Mock GPS mat tin hieu nem GPSSignalLostError"""
        mock_gps.side_effect = gps_service.GPSSignalLostError()
        result = self.app.get_nearby_restaurants()
        self.assertEqual(result, "Khong the xac dinh vi tri.")
        mock_gps.assert_called_once()


if __name__ == "__main__":
    unittest.main()
