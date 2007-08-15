from django.db import models
from django.conf import settings
import Image
from datetime import datetime
import shutil
from os import path
from fs import change_basename
import shutil, os, glob
from ella.core.models import Author, Source, Category
from ella.core.box import Box

# settings default
PHOTOS_FORMAT_QUALITY_DEFAULT = (
    (45, _('Low')),
    (65, _('Medium')),
    (75, _('Good')),
    (85, _('Better')),
    (95, _('High')),
)

PHOTOS_THUMB_DIMENSION_DEFAULT = (80,80)

PHOTOS_FORMAT_QUALITY = getattr(settings, 'PHOTOS_FORMAT_QUALITY', PHOTOS_FORMAT_QUALITY_DEFAULT)
PHOTOS_THUMB_DIMENSION = getattr(settings, 'PHOTOS_THUMB_DIMENSION', PHOTOS_THUMB_DIMENSION_DEFAULT)

# from: http://code.djangoproject.com/wiki/CustomUploadAndFilters
def auto_rename(file_path, new_name):
    """
    Renames a file, keeping the extension.

    Parameters:
    - file_path: the file path relative to MEDIA_ROOT
    - new_name: the new basename of the file (no extension)

    Returns the new file path on success or the original file_path on error.
    """
    # Return if no file given
    if file_path == '':
        return ''
    # Get the new name
    new_path = change_basename(file_path, new_name)

    # Changed?
    if new_path != file_path:
        # Try to rename
        try:
            shutil.move(os.path.join(settings.MEDIA_ROOT, file_path), os.path.join(settings.MEDIA_ROOT, new_path))
        except IOError:
            # Error? Restore original name
            new_path = file_path

    return new_path

class PhotoBox(Box):
    def get_context(self):
        cont = super(PhotoBox, self).get_context()
        cont.update({'title' : self.params.get('title', ''),  'alt' : self.params.get('alt', ''),})
        return cont

class Photo(models.Model):
    title = models.CharField(_('Title'), maxlength=200)
    description = models.TextField(_('Description'), blank=True)
    slug = models.CharField(maxlength=200, unique=True, db_index=True)
    image = models.ImageField(upload_to='photos/%Y/%m/%d', height_field='height', width_field='width') # save it to YYYY/MM/DD structure
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors') , related_name='photo_set')
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    created = models.DateTimeField(default=datetime.now, editable=False)


    def __unicode__(self):
        return self.title

    def thumb(self):
        """
        do thumbnails
        """
        tinythumb = path.split(self.image)
        tinythumb = (tinythumb[0] , 'thumb-' + tinythumb[1])
        tinythumb = path.join(*tinythumb)
        if not path.exists(settings.MEDIA_ROOT + tinythumb):
            try:
                im = Image.open(settings.MEDIA_ROOT + self.image)
                im.thumbnail(PHOTOS_THUMB_DIMENSION , Image.ANTIALIAS)
                im.save(settings.MEDIA_ROOT + tinythumb, "JPEG")
            except IOError:
                # TODO Logging something wrong
                return """<strong>%s</strong>""" % _('Thumbnail not available')
        return """<a href="%s%s"><img src="%s%s" alt="Thumbnail %s" /></a>""" % (settings.MEDIA_URL, self.image, settings.MEDIA_URL, tinythumb, self.title)
    thumb.allow_tags = True

    def Box(self, box_type, nodelist):
        return PhotoBox(self, box_type, nodelist)

    # TODO zajistit unikatnost nazvu slugu
    def save(self):
        while True:
            try:
                p = Photo.objects.get(slug=self.slug).exclude(pk=self.id)
                self.slug = '_' + self.slug
            except Photo.DoesNotExist:
                break

        self.image = auto_rename(self.image, self.slug)
        super(Photo, self).save()

    def ratio(self):
        if self.height:
            return float(self.width) / self.height
        else:
            return None

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')
        ordering = ('-created',)

class Format(models.Model):
    name = models.CharField(maxlength=80)
    max_width = models.PositiveIntegerField()
    max_height = models.PositiveIntegerField()
    stretch = models.BooleanField()
    resample_quality = models.IntegerField(choices=PHOTOS_FORMAT_QUALITY, default=85)

    def __unicode__(self):
        return  u"%s (%sx%s) " % (self.name, self.max_width, self.max_height)

    def ratio(self):
        if self.max_height:
            return float(self.max_width) / self.max_height
        else:
            return None

    class Meta:
        verbose_name = _('Format')
        verbose_name_plural = _('Formats')
        ordering = ('name', '-max_width',)

class FormatedPhoto(models.Model):
    photo = models.ForeignKey(Photo)
    format = models.ForeignKey(Format)
    filename = models.CharField(maxlength=300, editable=False) # derive local filename and url
    crop_left = models.PositiveIntegerField(default=0)
    crop_top = models.PositiveIntegerField(default=0)
    crop_width = models.PositiveIntegerField(default=0)
    crop_height = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    def __unicode__(self):
        return u"%s - %s" % (self.filename, self.format)

    def get_stretch_dimension(self):
        """ Method return stretch dimension of crop to fit inside max format rectangle """
        crop_ratio = float(self.crop_width) / self.crop_height
        if self.format.ratio() < crop_ratio :
            stretch_width = self.format.max_width
            stretch_height = min(self.format.max_height, int(stretch_width / crop_ratio)) # dimension must be integer
        else: #if(self.photo.ratio() < self.crop_ratio()):
            stretch_height = self.format.max_height
            stretch_width = min(self.format.max_width, int(stretch_height * crop_ratio))
        return (stretch_width, stretch_height)

    def save(self):
        source = Image.open(self.photo.get_image_filename())

        # if crop specified
        if self.crop_width and self.crop_height:
            # generate crop
            cropped_photo = source.crop((self.crop_left, self.crop_top, self.crop_left + self.crop_width, self.crop_top + self.crop_height))

        # else stay original
        else:
            self.crop_left, self.crop_top = 0, 0
            self.crop_width, self.crop_height = source.size
            cropped_photo = source

        # we don't have to resize the image if stretch isn't specified and the image fits within the format
        if not self.format.stretch and self.crop_width < self.format.max_width and self.crop_height < self.format.max_height:
            stretched_photo = cropped_photo

        # resize image to fit format
        else:
            stretched_photo = cropped_photo.resize(self.get_stretch_dimension(), Image.BICUBIC)

        self.width, self.height = stretched_photo.size
        self.filename = self.file(relative=True)
        stretched_photo.save(self.file(), quality=self.format.resample_quality)
        super(FormatedPhoto, self).save()


    # FIXME - formated photo is the same type as source photo eq. png => png, jpg => jpg
    def file(self, relative=False):
        """ Method returns formated photo path - derived from format.id and source Photo filename """
        if relative:
            source_file = path.split(self.photo.image)
        else:
            source_file = path.split(self.photo.get_image_filename())
        return path.join(source_file[0],  str (self.format.id) + '-' + source_file[1])

    class Meta:
        verbose_name = _('Formated photo')
        verbose_name_plural = _('Formated photos')
        unique_together = (('photo','format'),)

from django import newforms as forms
class FormatedPhotoForm(forms.BaseForm):
    def clean(self):
        """
        Validation function that checks the dimensions of the crop whether it fits into the original and the format.
        """
        data = self.cleaned_data
        photo = data['photo']
        if (
            data['crop_left'] >  photo.width or
            data['crop_top'] > photo.height or
            (data['crop_left'] + data['crop_width']) > photo.width or
            (data['crop_top'] + data['crop_height']) > photo.height
):
            raise forms.ValidationError, _("The specified crop coordinates do not fit into the source photo.")
        return data

from django.contrib import admin

class FormatOptions(admin.ModelAdmin):
    list_display = ('name', 'max_width', 'max_height', 'stretch', 'resample_quality',)

class PhotoOptions(admin.ModelAdmin):
    list_display = ('title', 'width', 'height', 'thumb') ## 'authors')
    list_filter = ('category', 'created',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'image', 'description',)

    def __call__(self, request, url):
        if url and url.endswith('json'):
            from ella.photos.views import format_photo_json
            return format_photo_json(request, *url.split('/')[-3:-1])
        return super(PhotoOptions, self).__call__(request, url)

class FormatedPhotoOptions(admin.ModelAdmin):
    base_form = FormatedPhotoForm
    list_display = ('filename', 'format', 'width', 'height')
    list_filter = ('format',)
    search_fields = ('filename',)
    raw_id_fields = ('photo',)

admin.site.register(Format, FormatOptions)
admin.site.register(Photo, PhotoOptions)
admin.site.register(FormatedPhoto, FormatedPhotoOptions)
