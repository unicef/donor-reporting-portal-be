from office365.runtime.utilities.http_method import HttpMethod
from office365.runtime.utilities.request_options import RequestOptions
from office365.sharepoint.file import File


class SharePointFile(File):

    @staticmethod
    def open_binary(ctx, server_relative_url):
        url = r"{}web/getfilebyserverrelativeurl('{}')/\$value".format(ctx.service_root_url, server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Get
        response = ctx.execute_request_direct(request)
        return response
