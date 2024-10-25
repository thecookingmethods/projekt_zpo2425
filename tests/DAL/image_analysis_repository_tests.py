import os.path
import shutil
import unittest

from DAL.image_analysis_repository import ImageAnalysisRepository
from models.exceptions.image_analysis_not_exists import ImageAnalysisNotExists
from models.image_analysis import ImageAnalysis


class ImageAnalysisRepositoryTests(unittest.TestCase):
    test_db_dir = './baza_do_testow'

    def setUp(self):
        if os.path.exists(self.test_db_dir):
            shutil.rmtree(self.test_db_dir)

    def tearDown(self):
        if os.path.exists(self.test_db_dir):
            shutil.rmtree(self.test_db_dir)

    def test_should_create_db_entry_while_creating_repo_object(self):
        self.assertFalse(os.path.exists(self.test_db_dir))

        repo = ImageAnalysisRepository(self.test_db_dir)

        self.assertTrue(os.path.exists(self.test_db_dir))

    def test_should_assign_id_1_and_create_entry(self):
        repo = ImageAnalysisRepository(self.test_db_dir)
        analysis = repo.create_analysis()

        self.assertEqual(analysis.id, 1)

        expected_entry_dir = os.path.join(self.test_db_dir, '1')
        self.assertTrue(os.path.exists(expected_entry_dir))

    def test_should_assign_next_id_and_create_entry(self):
        repo = ImageAnalysisRepository(self.test_db_dir)
        repo.create_analysis()

        analysis2 = repo.create_analysis()
        repo.create_analysis()
        repo.create_analysis()
        repo.create_analysis()
        repo.create_analysis()
        repo.create_analysis()
        repo.create_analysis()
        repo.create_analysis()
        repo.create_analysis()

        analysis11 = repo.create_analysis()

        self.assertEqual(analysis2.id, 2)
        expected_entry_dir = os.path.join(self.test_db_dir, '2')
        self.assertTrue(os.path.exists(expected_entry_dir))

        self.assertEqual(analysis11.id, 11)
        expected_entry_dir = os.path.join(self.test_db_dir, '11')
        self.assertTrue(os.path.exists(expected_entry_dir))

    def test_should_create_file_with_caption(self):
        repo = ImageAnalysisRepository(self.test_db_dir)
        analysis = repo.create_analysis()

        analysis.caption = "testowy opis"

        repo.update_analysis(analysis)

        expected_caption_path = os.path.join(self.test_db_dir, str(analysis.id), 'caption.txt')
        self.assertTrue(os.path.exists(expected_caption_path))

        with open(expected_caption_path, 'r') as f:
            self.assertEqual(f.read(), "testowy opis")

    def test_update_should_raise_exception_if_there_is_no_such_entry(self):
        repo = ImageAnalysisRepository(self.test_db_dir)

        analysis = ImageAnalysis(2, None)

        self.assertRaises(ImageAnalysisNotExists, repo.update_analysis, analysis)

    def test_get_should_raise_exception_if_there_is_not_such_entry(self):
        repo = ImageAnalysisRepository(self.test_db_dir)

        self.assertRaises(ImageAnalysisNotExists, repo.get_analysis, 2)

    def test_get_should_return_analysis_with_empty_caption_field_if_there_is_no_caption_file(self):
        repo = ImageAnalysisRepository(self.test_db_dir)
        analysis1 = repo.create_analysis()

        analysis_from_repo = repo.get_analysis(analysis1.id)

        self.assertIsNone(analysis_from_repo.caption)

    def test_get_should_return_analysis_with_caption_field_if_there_is_a_caption_file(self):
        repo = ImageAnalysisRepository(self.test_db_dir)
        analysis1 = repo.create_analysis()
        analysis1.caption = "testowy opis"
        repo.update_analysis(analysis1)

        analysis_from_repo = repo.get_analysis(analysis1.id)

        self.assertEqual(analysis_from_repo.caption, "testowy opis")
    