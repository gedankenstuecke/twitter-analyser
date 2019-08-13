import os

from django.test import TestCase

from ..read_data import create_main_dataframe, read_files
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

        new_filename = 'new_tweet_subset.js'
        new_test_file = os.path.join(current_dir, new_filename)

        self.df = create_main_dataframe(test_file)
        self.new_df = read_files(open(new_test_file, 'r'), 'json')[0]
        self.new_df = self.new_df.sort_values('utc_time', ascending=False)
        self.new_df = self.new_df.set_index('utc_time')
        self.new_df = self.new_df.replace(to_replace={
                                        'url': {False: None},
                                        'hashtag': {False: None},
                                        'media': {False: None}
                                        })

    def test_create_hourly_stats(self):
        stats = create_hourly_stats(self.df)
        self.assertEquals(stats.shape, (20, 4))


    def test_create_heatmap(self):
        heatmap = create_heatmap(self.df)
        self.assertEquals(heatmap.shape, (469, 2))
        new_heatmap = create_heatmap(self.new_df)
        self.assertEquals(new_heatmap.shape, (0, 2))


    def test_create_overall(self):
        overall = create_overall(self.df)
        self.assertEquals(overall.shape, (62, 2))
        new_overall = create_overall(self.new_df)
        self.assertEquals(new_overall.shape, (4, 2))

    def test_create_timeline(self):
        timeline = create_timeline(self.df)
        self.assertEquals(len(timeline), 78186)

    def test_top_replies(self):
        replies = create_top_replies(self.df)
        self.assertEquals(replies.shape, (2, 6))

    def test_top_types(self):
        types = create_tweet_types(self.df)
        self.assertEquals(types.shape, (62, 9))
