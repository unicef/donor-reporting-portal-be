# from donor_reporting_portal.libraries.sharepoint.client import SharePointClient
#
#
# class TestShareP  ointAPI:
#
#     def test_download(self):
#
#         client = SharePointClient()
#
#         files = client.read_files('Documents')
#         sh_file = files[0]
#
#         ppp = sh_file.properties['ServerRelativeUrl']
#
#         # filename = "User Guide.docx"
#         # import pdb; pdb.set_trace()
#         ppp = 'Shared Documents/Test.docx'
#         import pdb;
#         pdb.set_trace()
#         res = File.open_binary(self.client.context, ppp)
#         # response = File.open_binary(self.client.context, "/Shared Documents/%s" % filename)
#         # with open("./%s" % filename, "wb") as local_file:
#         #     local_file.write(response.content)
#         # import pdb; pdb.set_trace()
#         response = HttpResponse(res.content)
#         response['Content-Disposition'] = 'attachment; filename=pippo.docx'
#         return response
#
#     # c = ApiClient()
