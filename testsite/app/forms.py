import csv
import io
from django import forms
from django.core.validators import FileExtensionValidator
from .models import Post


class CSVUploadForm(forms.Form):
    file = forms.FileField(
        label='CSVファイル',
        help_text='※拡張子csvのファイルをアップロードしてください。',
        validators=[FileExtensionValidator(allowed_extensions=['csv'])]
    )

    def clean_file(self):
        file = self.cleaned_data['file']

        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
        csv_file = io.TextIOWrapper(file, encoding='utf-8')
        reader = csv.reader(csv_file)

        # 各行から作った保存前のモデルインスタンスを保管するリスト
        self._instances = []
        try:
            for row in reader:
                post = Post(pk=row[0], title=row[1])
                self._instances.append(post)
        except UnicodeDecodeError:
            raise forms.ValidationError('ファイルのエンコーディングや、正しいCSVファイルか確認ください。')

        return file

    def save(self):
        Post.objects.bulk_create(self._instances, ignore_conflicts=True)
        Post.objects.bulk_update(self._instances, fields=['title'])
