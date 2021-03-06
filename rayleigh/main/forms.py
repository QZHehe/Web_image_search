# -*- coding: UTF-8 -*-
# encoding = utf-8
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField
from auth.forms import Province_choice
from pymongo import MongoClient
from wtforms import ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_pagedown.fields import PageDownField
from collection import collection_image,collection_user


class EditProfileForm(FlaskForm):
    name = StringField('姓名', validators=[Length(0, 64)])
    location = SelectField('地址', choices=Province_choice)
    about_me = TextAreaField('自我介绍', validators=[Length(0, 64)])
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
    choices = [('Administrator', '管理员'), ('Moderator', '协管员'), ('User', '用户')]
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                          Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          '支持英文和字母下划线.')])
    activate = BooleanField('账户激活状态')
    role = SelectField('权限', choices=choices)
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('自我介绍')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_email(self, field):
        if field.data == self.user.username:
            return
        if collection_user.User.find_one({'temp': field.data}):
            raise ValidationError('邮箱已被注册.')

    def validate_username(self, field):
        if field.data == self.user.username:
            return
        if collection_user.User.find_one({'username': field.data}):
            raise ValidationError('用户名已被注册.')


class PostForm(FlaskForm):
    body = PageDownField('有什么想说的吗？', validators=[Required()])
    # image = FileField('上传图片',validators=[
    #     FileField(),
    #     FileAllowed(['jpg','png'])
    # ])
    submit = SubmitField('发表')


class PostImageForm(FlaskForm):

    image = FileField('上传图片',validators=[
        FileRequired('文件未选择!'),
        FileAllowed(['jpg','png','JPG'],'只能上传图片')
    ])
    text = PageDownField('图片说明', validators=[Required()])
    submit = SubmitField('发表')


class EditPostForm(FlaskForm):
    body = PageDownField('', validators=[Required()])
    submit = SubmitField('修改')


class EditPostImageForm(FlaskForm):
    body = PageDownField('', validators=[Required()])
    submit = SubmitField('修改')


class CommentForm(FlaskForm):
    body = StringField('', validators=[Required()])
    submit = SubmitField('发布')


class PostImagesForm(FlaskForm):

    image = FileField('批量上传图片',validators=[
        FileRequired('文件未选择!'),
        FileAllowed(['jpg','png','JPG'],'只能上传图片')
    ])
    text = PageDownField('图片说明', validators=[Required()])
    show = BooleanField('前端显示')
    submit = SubmitField('发表')