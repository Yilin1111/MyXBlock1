"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from xblock.core import XBlock
from xblock.fields import Integer, Scope ,String
from xblock.fragment import Fragment


class TestVideoXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    count = Integer(
        default=0, scope=Scope.user_state,
        help="A simple counter, to show something happening",
    )

    src = String(help="URL of the video page at the provider", default=None, scope=Scope.content)
    width = Integer(help="width of the video", default=800, scope=Scope.content)
    height = Integer(help="height of the video", default=450, scope=Scope.content)


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the TestVideoXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/testvideoxblock.html")
        frag = Fragment(html.format(src=self.src, width=self.width, height=self.height))
        frag.add_css(self.resource_string("static/css/testvideoxblock.css"))
        return frag

    def studio_view(self, context):
        """
        Create a fragment used to display the edit view in the Studio.
        """
        html_str = self.resource_string("static/html/video_edit.html")
        src = self.src or ''
        frag = Fragment(unicode(html_str).format(src=src, width=self.width, height=self.height))
        frag.add_javascript(self.resource_string("static/js/src/testvideoxblock.js"))
        frag.initialize_js('TestVideoXBlock')
        return frag

    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.src = data.get('src')
        self.width = data.get('width')
        self.height = data.get('height')

        return {'result': 'success'}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("TestVideoXBlock",
             """<testvideoxblock/>
             """),
            ("Multiple TestVideoXBlock",
             """<vertical_demo>
                <testvideoxblock/>
                <testvideoxblock/>
                <testvideoxblock/>
                </vertical_demo>
             """),
        ]
