import os

from django.test import TestCase

from ..read_data import create_main_dataframe
from ..analyse_data import create_heatmap, \
    create_hourly_stats, \
    create_overall, \
    create_timeline, \
    create_top_replies, \
    create_tweet_types


class DataTestCase(TestCase):
    """
    Test cases for data loading and analysis. Uses only two months,
    December 2016 and January 2017, from test_archive.zip.
    """

    def setUp(self):
        file_name = 'test_archive_2016_2017_2_months.zip'
        current_dir = os.path.dirname(os.path.realpath('__file__'))
        test_file = os.path.join(current_dir, file_name)
        self.df = create_main_dataframe(test_file)

    def test_create_hourly_stats(self):
        stats = create_hourly_stats(self.df)
        self.assertEquals(stats.shape, (20, 4))

    def test_create_heatmap(self):
        heatmap = create_heatmap(self.df)
        self.assertEquals(heatmap.shape, (469, 2))

    def test_create_overall(self):
        overall = create_overall(self.df)
        self.assertEquals(overall.shape, (62, 2))

    def test_create_timeline(self):
        timeline = create_timeline(self.df)
        self.assertEquals(len(timeline), 78186)

    def test_top_replies(self):
        replies = create_top_replies(self.df)
        self.assertEquals(replies.shape, (2, 6))

    def test_top_types(self):
        types = create_tweet_types(self.df)
        self.assertEquals(types.shape, (62, 9))
