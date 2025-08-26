from django.contrib import admin
from .models import Municipality, Category, Complaint, Status ,Ward ,Comment
from .forms import ComplaintAdminForm 

class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

class WardAdmin(admin.ModelAdmin):
    list_display = ['id', 'municipality', 'get_municipality_id', 'ward_number']
    list_filter = ['municipality']

    def get_municipality_id(self, obj):
        return obj.municipality.id
    get_municipality_id.short_description = 'Municipality ID'
    
class ComplaintAdmin(admin.ModelAdmin):
    form = ComplaintAdminForm

    list_display = [
        'id', 'title','description','municipality', 'ward', 'status', 'user', 'is_hidden', 
        'report_count', 'like_count', 'comment_count'
    ]
    list_editable = ['title','description', 'municipality', 'ward', 'status', 'is_hidden']
    list_filter = ['municipality', 'status', 'is_hidden']
    search_fields = ['title', 'description']

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'user', 'municipality', 'ward', 'category', 'status', 'is_hidden')
        }),
        ('Counts', {
            'fields': ('report_count', 'like_count', 'comment_count'),
            'classes': ('collapse',)  # optional: collapse counts as they are read-only stats
        }),
    )

    readonly_fields = ('report_count', 'like_count', 'comment_count')
    
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id','content','user' ,'complaint']
    list_editable = ['content']
    



admin.site.register(Municipality, MunicipalityAdmin)
admin.site.register(Ward, WardAdmin)
admin.site.register(Category)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(Status)
admin.site.register(Comment , CommentAdmin)
