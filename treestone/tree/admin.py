from django.contrib import admin

#Register your models here.
from treestone.tree.models import Bibliography, CitationStone, CitationTree
from treestone.tree.models import Stones, StoneImages, StoneEdits
from treestone.tree.models import Trees, TreeImages, TreeEdits
from import_export.admin import ImportExportModelAdmin


class TreesAdmin(ImportExportModelAdmin):
    list_display = ('common_name',)
    search_fields = ('common_name', 'sci_name',)
    #list_display changes what is visible once you add data to your django admin
class BibliographyAdmin(ImportExportModelAdmin):
    list_display = ('full_citation', 'notes') 
    search_fields = ('full_citation', 'notes') 
'''
class CitationAdmin(admin.ModelAdmin):
    list_display = ('url','notes')
    search_fields = ('url','notes')
'''    
class CitationStoneAdmin(ImportExportModelAdmin):
    list_display = ('stone_attribute','notes')
    search_fields = ('stone_attribute','notes')
class CitationTreeAdmin(ImportExportModelAdmin):
    list_display = ('tree_attribute','notes')
    search_fields = ('tree_attribute','notes')
class StonesAdmin(ImportExportModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
class TreeEditsAdmin(ImportExportModelAdmin):
    list_display=('get_name',)

    def get_name(self, obj): 
        if obj.main_object: 
            return obj.main_object.common_name
        else:
            return obj.common_name
class StoneEditsAdmin(ImportExportModelAdmin):
    list_display=('get_name',)

    def get_name(self, obj): 
        if obj.main_object: 
            return obj.main_object.name
        else:
            return obj.name


admin.site.register(Trees, TreesAdmin)
admin.site.register(Bibliography, BibliographyAdmin)
#admin.site.register(Citation, CitationAdmin)
admin.site.register(CitationStone, CitationStoneAdmin)
admin.site.register(CitationTree, CitationTreeAdmin)
admin.site.register(Stones, StonesAdmin)
admin.site.register(StoneImages)
admin.site.register(TreeImages)
admin.site.register(TreeEdits, TreeEditsAdmin)
admin.site.register(StoneEdits, StoneEditsAdmin)


