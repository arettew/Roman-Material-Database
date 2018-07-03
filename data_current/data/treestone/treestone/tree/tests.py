from django.test import TestCase, RequestFactory
from treestone.tree.models import Trees, Stones

import json

# Create your tests here.

class TestTreeViews(TestCase):
    def setUp(self): 
        self.factory = RequestFactory()
        Trees.objects.create(common_name="fake_tree", geojson="fake_geojson")
        Stones.objects.create(name="fake_stone", geojson="fake_geojson")
    
    def test_get_details_trees(self): 
        # Shouldn't be in response 
        Trees.objects.create(common_name="bad_tree", geojson="")
        targetJson = json.dumps({'fake_tree': {'geojson': 'fake_geojson'}})

        response = self.client.post('/get_features/', {'type': 'trees'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, targetJson)

    def test_get_details_stones(self):
        # Shouldn't be in response
        Stones.objects.create(name="bad_stone", geojson="")
        targetJson = json.dumps({'fake_stone': {'geojson': 'fake_geojson'}})

        response = self.client.post('/get_features/', {'type': 'stones'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, targetJson)

    def test_get_details_stones_date(self):
        stone = Stones.objects.get(name="fake_stone")
        stone.start_date = "100 BCE"
        stone.end_date = "100 AD"  
        stone.save()
        targetJson = json.dumps({'fake_stone': {'geojson': 'fake_geojson', 'start_date': -100, 'end_date': 100}})

        response = self.client.post('/get_features/', {'type': 'stones'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, targetJson)
        
