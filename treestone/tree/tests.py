from django.test import TestCase, RequestFactory
from treestone.tree.models import Trees, Stones, TreeEdits, StoneEdits
from django.contrib.auth.models import User 
from django.core.urlresolvers import reverse

import json, StringIO 

# Create your tests here.

class TestMapFunctions(TestCase):
    def setUp(self): 
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

    def test_get_geojson_file(self):
        pk = Trees.objects.get(common_name="fake_tree").pk

class TestWebPages(TestCase):
    def setUp(self):
        Trees.objects.create(common_name="fake_tree", geojson="fake_geojson")
        tree = Trees.objects.get(common_name="fake_tree")
        TreeEdits.objects.create(main_object=tree)

        Stones.objects.create(name="fake_stone", geojson="fake_geojson")
        stone = Stones.objects.get(name="fake_stone")
        StoneEdits.objects.create(main_object=stone)

        User.objects.create_user(username="user", password="password")
        User.objects.create_user(username="staff", password="password", is_staff=True)
         
    def test_map_page(self): 
        response = self.client.get('/map/')
        self.assertEqual(response.status_code, 200) 

    def test_edit_page_stone(self): 
        self.client.login(username="user", password="password")
        pk = Stones.objects.get(name="fake_stone").pk
        response = self.client.get('/stones/edit/' + str(pk) + '/')
        self.assertEqual(response.status_code, 200)
    
    def test_edit_page_tree(self): 
        self.client.login(username="user", password="password")
        pk = Trees.objects.get(common_name="fake_tree").pk
        response = self.client.get('/trees/edit/' + str(pk) + '/')
        self.assertEqual(response.status_code, 200)

    def test_edit_page_stone_not_logged_in(self): 
        pk = Stones.objects.get(name="fake_stone").pk
        response = self.client.get('/stones/edit/' + str(pk) + '/')
        self.assertEqual(response.status_code, 302)
    
    def test_edit_page_tree_not_logged_in(self): 
        pk = Trees.objects.get(common_name="fake_tree").pk
        response = self.client.get('/trees/edit/' + str(pk) + '/')
        self.assertEqual(response.status_code, 302)

    def test_edits_list_page(self): 
        self.client.login(username="staff", password="password")
        response = self.client.get("/edits-list/")
        self.assertEqual(response.status_code, 200)

    def test_edits_approval_tree(self): 
        self.client.login(username="staff", password="password")
        pk = TreeEdits.objects.get(main_object__common_name="fake_tree").pk
        response = self.client.get("/trees/approve/" + str(pk) + "/")
        self.assertEqual(response.status_code, 200)
    
    def test_edits_approval_stone(self):
        self.client.login(username="staff", password="password")
        pk = StoneEdits.objects.get(main_object__name="fake_stone").pk
        response = self.client.get("/stones/approve/" + str(pk) + "/")
        self.assertEqual(response.status_code, 200) 
    
    def test_edits_list_page_logout(self): 
        response = self.client.get("/edits-list/")
        self.assertEqual(response.status_code, 302)
    
    def test_edits_approval_tree_logout(self): 
        pk = TreeEdits.objects.get(main_object__common_name="fake_tree").pk
        response = self.client.get("/trees/approve/" + str(pk) + "/")
        self.assertEqual(response.status_code, 302)
    
    def test_edits_approval_stone_logout(self):
        pk = StoneEdits.objects.get(main_object__name="fake_stone").pk
        response = self.client.get("/stones/approve/" + str(pk) + "/")
        self.assertEqual(response.status_code, 302) 
    
    def test_edits_list_page_regular_user(self): 
        self.client.login(username="user", password="password")
        response = self.client.get("/edits-list/")
        self.assertEqual(response.status_code, 302)

    def test_edits_approval_tree_regular_user(self): 
        self.client.login(username="user", password="password")
        pk = TreeEdits.objects.get(main_object__common_name="fake_tree").pk
        response = self.client.get("/trees/approve/" + str(pk) + "/")
        self.assertEqual(response.status_code, 302)
    
    def test_edits_approval_stone_regular_user(self):
        self.client.login(username="user", password="password")
        pk = StoneEdits.objects.get(main_object__name="fake_stone").pk
        response = self.client.get("/stones/approve/" + str(pk) + "/")
        self.assertEqual(response.status_code, 302) 
    

class TestEdits(TestCase): 
    def setUp(self):
        Trees.objects.create(common_name="fake_tree", geojson="fake_geojson")
        tree = Trees.objects.get(common_name="fake_tree")
        TreeEdits.objects.create(main_object=tree, common_name="edit")

        Stones.objects.create(name="fake_stone", geojson="fake_geojson")
        stone = Stones.objects.get(name="fake_stone")
        StoneEdits.objects.create(main_object=stone, name="edit")

        User.objects.create_user(username="staff", password="password", is_staff=True)
        User.objects.create_user(username="user", password="password", is_staff=True)

    def test_edit_creation_tree(self): 
        self.client.login(username="user", password="password")
        tree = Trees.objects.get(common_name="fake_tree")
        response = self.client.post(
            "/trees/edit/" + str(tree.pk) + "/",
            {"main_object": tree, "common_name":"fake_tree", "sci_name": "sci_name"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TreeEdits.objects.filter(sci_name="sci_name").exists())

    def test_edit_creation_stone(self): 
        self.client.login(username="user", password="password")
        stone = Stones.objects.get(name="fake_stone")
        response = self.client.post(
            reverse("stone-update", kwargs={"pk": stone.pk}),
            {"main_object": stone, "name": "fake_stone", "alternate_name": "alt_name"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(StoneEdits.objects.filter(alternate_name="alt_name").exists())
    
    def test_edit_creation_tree_good_geojson(self):
        self.client.login(username="user", password="password")
        tree = Trees.objects.get(common_name="fake_tree") 
        geojsonFile = StringIO.StringIO('{"geometry": {"type": "Point", "coordinates": [0, 0]}, "type": "Feature", "properties": {}}')
        geojsonFile.name = "test.geojson"

        response = self.client.post(
            reverse("tree-update", kwargs={"pk": tree.pk}),
            {"main_object": tree, "common_name": "fake_tree", "sci_name": "sci_name", "geojson_file": geojsonFile})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(TreeEdits.objects.filter(sci_name="sci_name").exists())

    def test_edit_creation_new_stone(self): 
        self.client.login(username="user", password="password")
        response = self.client.post(
            '/stones/create/',
            {"name": "new_stone"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(StoneEdits.objects.filter(name="new_stone").exists())
    
    def test_edit_creation_new_tree(self): 
        self.client.login(username="user", password="password")
        response = self.client.post(
            '/trees/create/',
            {"common_name": "new_tree"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TreeEdits.objects.filter(common_name="new_tree").exists())

    def test_edit_creation_new_stone_same_name(self): 
        self.client.login(username="user", password="password")
        response = self.client.post(
            '/stones/create/',
            {"name": "fake_stone"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(StoneEdits.objects.filter(name="fake_stone").exists())
    
    def test_edit_creation_new_tree_same_common_name(self): 
        self.client.login(username="user", password="password")
        response = self.client.post(
            '/trees/create/',
            {"common_name": "fake_tree"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TreeEdits.objects.filter(common_name="fake_tree").exists())

    def test_edit_creation_stone_good_geojson(self):
        self.client.login(username="user", password="password")
        stone = Stones.objects.get(name="fake_stone") 
        geojsonFile = StringIO.StringIO('{"geometry": {"type": "Point", "coordinates": [0, 0]}, "type": "Feature", "properties": {}}')
        geojsonFile.name = "test.geojson"

        response = self.client.post(
            reverse("stone-update", kwargs={"pk": stone.pk}),
            {"main_object": stone, "name": "fake_stone", "alternate_name": "alt_name", "geojson_file": geojsonFile})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(StoneEdits.objects.filter(alternate_name="alt_name").exists())
    
    def test_edit_creation_tree_bad_geojson(self):
        self.client.login(username="user", password="password")
        tree = Trees.objects.get(common_name="fake_tree") 
        geojsonFile = StringIO.StringIO('{"geometry": {"type": "Point"}, "type": "Feature", "properties": {}}')
        geojsonFile.name = "test.geojson"

        response = self.client.post(
            reverse("tree-update", kwargs={"pk": tree.pk}),
            {"main_object": tree, "sci_name": "sci_name", "geojson_file": geojsonFile})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(TreeEdits.objects.filter(sci_name="sci_name").exists())

    def test_edit_creation_stone_bad_geojson(self):
        self.client.login(username="user", password="password")
        stone = Stones.objects.get(name="fake_stone") 
        geojsonFile = StringIO.StringIO('{"geometry": {"type": "Point"}, "type": "Feature", "properties": {}}')
        geojsonFile.name = "test.geojson"

        response = self.client.post(
            reverse("stone-update", kwargs={"pk": stone.pk}),
            {"main_object": stone, "alternate_name": "alt_name", "geojson_file": geojsonFile})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(StoneEdits.objects.filter(alternate_name="alt_name").exists())

    def test_edit_creation_tree_not_geojson_file(self):
        self.client.login(username="user", password="password")
        tree = Trees.objects.get(common_name="fake_tree") 
        geojsonFile = StringIO.StringIO('{"geometry": {"type": "Point", "coordinates": [0, 0]}, "type": "Feature", "properties": {}}')
        geojsonFile.name = "test"

        response = self.client.post(
            reverse("tree-update", kwargs={"pk": tree.pk}),
            {"main_object": tree, "sci_name": "sci_name", "geojson_file": geojsonFile})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(TreeEdits.objects.filter(sci_name="sci_name").exists())

    def test_edit_creation_stone_not_geojson_file(self):
        self.client.login(username="user", password="password")
        stone = Stones.objects.get(name="fake_stone") 
        geojsonFile = StringIO.StringIO('{"geometry": {"type": "Point", "coordinates": [0, 0]}, "type": "Feature", "properties": {}}')
        geojsonFile.name = "test"

        response = self.client.post(
            reverse("stone-update", kwargs={"pk": stone.pk}),
            {"main_object": stone, "alternate_name": "alt_name", "geojson_file": geojsonFile})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(StoneEdits.objects.filter(alternate_name="alt_name").exists())

    def test_edit_creation_tree_not_json(self):
        self.client.login(username="user", password="password")
        tree = Trees.objects.get(common_name="fake_tree") 
        geojsonFile = StringIO.StringIO('This is not json')
        geojsonFile.name = "test.geojson"

        response = self.client.post(
            reverse("tree-update", kwargs={"pk": tree.pk}),
            {"main_object": tree, "sci_name": "sci_name", "geojson_file": geojsonFile})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(TreeEdits.objects.filter(sci_name="sci_name").exists())

    def test_edit_creation_stone_not_json(self):
        self.client.login(username="user", password="password")
        stone = Stones.objects.get(name="fake_stone") 
        geojsonFile = StringIO.StringIO('This is not json')
        geojsonFile.name = "test.geojson"

        response = self.client.post(
            reverse("stone-update", kwargs={"pk": stone.pk}),
            {"main_object": stone, "alternate_name": "alt_name", "geojson_file": geojsonFile})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(StoneEdits.objects.filter(alternate_name="alt_name").exists())
    
    def test_edit_accept_stone(self): 
        self.client.login(username="staff", password="password")
        edit = StoneEdits.objects.get(main_object__name="fake_stone")
        response = self.client.post(
            reverse("stone-edit-approve", kwargs={"pk": edit.pk}),
            {"decision": "approve"})

        self.assertRedirects(response, "/edits-list/")
        self.assertTrue(Stones.objects.filter(name="edit").exists())
        self.assertFalse(Stones.objects.filter(name="fake_stone").exists())
        self.assertEquals(StoneEdits.objects.all().count(), 0)
        self.assertEquals(Stones.objects.all().count(), 1)
    
    def test_edit_reject_stone(self): 
        self.client.login(username="staff", password="password")
        edit = StoneEdits.objects.get(main_object__name="fake_stone")
        response = self.client.post(
            reverse("stone-edit-approve", kwargs={"pk": edit.pk}),
            {"decision": "reject"})

        self.assertRedirects(response, "/stones/approve/reject/" + str(edit.pk) + "/")
    
    def test_edit_accept_tree(self): 
        self.client.login(username="staff", password="password")
        edit = TreeEdits.objects.get(main_object__common_name="fake_tree")
        response = self.client.post(
            reverse("tree-edit-approve", kwargs={"pk": edit.pk}),
            {"decision": "approve"})

        self.assertRedirects(response, "/edits-list/")
        self.assertTrue(Trees.objects.filter(common_name="edit").exists())
        self.assertFalse(Trees.objects.filter(common_name="fake_tree").exists())
        self.assertEquals(TreeEdits.objects.all().count(), 0)
        self.assertEquals(Trees.objects.all().count(), 1)

    def test_edit_reject_tree(self): 
        self.client.login(username="staff", password="password")
        edit = TreeEdits.objects.get(main_object__common_name="fake_tree")
        response = self.client.post(
            reverse("tree-edit-approve", kwargs={"pk": edit.pk}),
            {"decision": "reject"})

        self.assertRedirects(response, "/trees/approve/reject/" + str(edit.pk) + "/")
    
    def test_multiple_edits_accept_tree(self):
        self.client.login(username="staff", password="password")
        tree = Trees.objects.get(common_name="fake_tree")
        TreeEdits.objects.create(main_object=tree, common_name="edit_one")
        TreeEdits.objects.create(main_object=tree, common_name="edit_two")
        
        edit = TreeEdits.objects.get(common_name="edit")
        response = self.client.post(
            reverse("tree-edit-approve", kwargs={"pk": edit.pk}),
            {"decision": "approve"})

        for treeEdit in TreeEdits.objects.all():
            self.assertEqual(treeEdit.main_object, tree)
        self.assertEqual(TreeEdits.objects.all().count(), 2)
    
    def test_multiple_edits_accept_stone(self):
        self.client.login(username="staff", password="password")
        stone = Stones.objects.get(name="fake_stone")
        StoneEdits.objects.create(main_object=stone, name="edit_one")
        StoneEdits.objects.create(main_object=stone, name="edit_two")
        
        edit = StoneEdits.objects.get(name="edit")
        response = self.client.post(
            reverse("stone-edit-approve", kwargs={"pk": edit.pk}),
            {"decision": "approve"})

        for stoneEdit in StoneEdits.objects.all():
            self.assertEqual(stoneEdit.main_object, stone)
        self.assertEqual(StoneEdits.objects.all().count(), 2)