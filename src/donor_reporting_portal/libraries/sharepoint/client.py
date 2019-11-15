import logging
import os

from django.conf import settings

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.caml_query import CamlQuery
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.file import File
from office365.sharepoint.file_creation_information import FileCreationInformation

from donor_reporting_portal.libraries.sharepoint.querystring_builder import QueryStringBuilder

logger = logging.getLogger(__name__)


class SharePointClientException(Exception):
    """SharePoint Exception when initializing the client"""


class SharePointClient:
    """Client to access SharePoint Document Library"""

    def __init__(self, *args, **kwargs) -> None:

        self.site_path = kwargs.get('url', settings.SHAREPOINT_TENANT['url'])
        self.relative_url = kwargs.get('relative_url', settings.SHAREPOINT_TENANT['url'])
        username = kwargs.get('username', settings.SHAREPOINT_TENANT['user_credentials']['username'])
        password = kwargs.get('password', settings.SHAREPOINT_TENANT['user_credentials']['password'])
        self.folder = kwargs.get('folder_name', 'Documents')

        ctx_auth = AuthenticationContext(url=self.site_path)
        if ctx_auth.acquire_token_for_user(username=username, password=password):
            self.context = ClientContext(self.site_path, ctx_auth)
        else:
            logger.exception(ctx_auth.get_last_error())
            raise SharePointClientException(ctx_auth.get_last_error())

    def get_querystring(self, filters):
        return QueryStringBuilder(filters).get_querystring()

    def get_folder(self, list_title):
        list_obj = self.context.web.lists.get_by_title(list_title)
        folder = list_obj.root_folder
        self.context.load(folder)
        self.context.execute_query()
        logger.info(f'List url: {folder.properties["ServerRelativeUrl"]}')
        return folder

    def read_folders(self, list_title):
        self.get_folder(list_title)
        folders = self.context.web.folders
        self.context.load(folders)
        self.context.execute_query()
        for folder in folders:
            logger.info(f'Folder name: {folder.properties["Name"]}')

        return folders

    def read_files(self, filters=dict()):
        querystring = self.get_querystring(filters)
        folder = self.get_folder(self.folder)
        files = folder.files.filter(querystring)
        self.context.load(files)
        self.context.execute_query()
        for cur_file in files:
            logger.info(f'File name: {cur_file.properties["Name"]}')

        return files

    def read_items(self, filters=dict()):
        querystring = self.get_querystring(filters)
        list_object = self.context.web.lists.get_by_title(self.folder)
        items = list_object.get_items().filter(querystring)
        self.context.load(items)
        self.context.execute_query()
        return items

    def read_file(self, filename):
        folder = self.get_folder(self.folder)
        cur_file = folder.files.get_by_url(f'/{self.relative_url}/{self.folder}/{filename}.pdf')
        self.context.load(cur_file)
        self.context.execute_query()
        logger.info(f'File name: {cur_file.properties["Name"]}')
        return cur_file

    def read_folder_and_files_alt(self, list_title='Documents'):
        """Read a folder example"""
        list_obj = self.context.web.lists.get_by_title(list_title)
        qry = CamlQuery.create_all_items_query()
        items = list_obj.get_items(qry)
        self.context.load(items)
        self.context.execute_query()
        for cur_item in items:
            logger.info('File name: {cur_item.properties["Title"]}')

    def upload_file_alt(self, target_folder, name, content):
        context = target_folder.context
        info = FileCreationInformation()
        info.content = content
        info.url = name
        info.overwrite = True
        target_file = target_folder.files.add(info)
        context.execute_query()
        return target_file

    def upload_file(self, path, list_title='Documents', upload_into_library=True):
        with open(path, 'rb') as content_file:
            file_content = content_file.read()

        if upload_into_library:
            target_folder = self.context.web.lists.get_by_title(list_title).root_folder
            file = self.upload_file_alt(target_folder, os.path.basename(path), file_content)
            logger.info('File url: {}'.format(file.properties['ServerRelativeUrl']))
        else:
            target_url = f'/{self.folder}/{os.path.basename(path)}'
            File.save_binary(self.context, target_url, file_content)

    def download_file(self, filename):
        response = File.open_binary(self.context, f'/{self.folder}/{filename}')
        with open(f'./data/{filename}', 'wb') as local_file:
            local_file.write(response.content)
