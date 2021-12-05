from functools import reduce

from django.http import FileResponse


class TXTDownload:
    def download(self, downloadlist, header):
        title = header + '\n\n'
        plot = reduce(lambda akk, s: akk + f'* {s}\n', downloadlist, title)
        result = FileResponse(plot, as_attachment=True, filename='dowload.txt')
        result.headers['Content-Type'] = 'plain/text'
        return result
