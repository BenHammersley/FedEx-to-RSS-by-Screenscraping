#!/usr/bin/perl -w
# RSS generator from FedEx Tracker
# Ben Hammersley
# Change Log:
# 7 July added non-breaking-space stripping for working in Windows systems
# 14 Oct Jorge Velazquez fixed URL and table format changes


use strict;
use XML::RSS;
use CGI qw(:standard);
use LWP::Simple 'get';
use HTML::TokeParser;

my ($tag, $headline, $url, $date_line);
my $last_good_date;
my $table_end_check;

my $cgi = CGI::new();
my $tracking_number = $cgi->param('track');

my $tracking_page = 
get("http://fedex.com/Tracking?action=track&tracknumber_list=$tracking_number&cntry_code=us");

my $stream = HTML::TokeParser->new(\$tracking_page);

my $rss = XML::RSS->new();

$rss->channel( title => "FedEx Tracking: $tracking_number",
link => "http://fedex.com/Tracking?action=track&tracknumber_list=$tracking_number&cntry_code=us");

# Go to the right part of the page, skipping 13 tables (!!!)
$stream->get_tag("table");
$stream->get_tag("table");
$stream->get_tag("table");
$stream->get_tag("table");
$stream->get_tag("table");
$stream->get_tag("table");
$stream->get_tag("table");
$stream->get_tag("table");
$stream->get_tag("table");
$stream->get_tag("table");
$stream->get_tag("table");
$stream->get_tag("table");
$stream->get_tag("table");

# Now go inside the tracking details table
$stream->get_tag("table");
$stream->get_tag("tr");
$stream->get_tag("/tr");
$stream->get_tag("tr");
$stream->get_tag("/tr");

# Now we loop through the table, getting the dates and locations. We need to stop at the bottom of the table, so we test for a closing /table tag.

PARSE: while ($tag = $stream->get_tag('tr')) {

$stream->get_tag("td");
$stream->get_tag("/td");

# Test here for the closing /tr. If it exists, we're done.


# Now get date text
$stream->get_tag("td");
$stream->get_tag("b");

my $date_text = $stream->get_trimmed_text("/b");

# The page only mentions the date once, so we need to fill in the blanks
if ($date_text eq "\xa0") {
$date_text = $last_good_date;
} else {
$last_good_date = $date_text
};

# Now get the time text
$stream->get_tag("/b");
$stream->get_tag("/td");
$stream->get_tag("td");
my $time_text = $stream->get_trimmed_text("/td");
$time_text =~ s/\xa0//g;


# Now get the status
$stream->get_tag("/td");
$stream->get_tag("/td");
$stream->get_tag("/td");
$stream->get_tag("/td");
$stream->get_tag("td");
my $status = $stream->get_trimmed_text("/td");
$status =~ s/\xa0//g;

# Now get the location
$stream->get_tag("/td");
$stream->get_tag("/td");
$stream->get_tag("/td");
$stream->get_tag("/td");
$stream->get_tag("td");
my $location = $stream->get_trimmed_text("/td");
$location =~ s/\xa0//g;

# Now get the comment
$stream->get_tag("/td");
$stream->get_tag("/td");
$stream->get_tag("/td");
$stream->get_tag("/td");
$stream->get_tag("td");
my $comment = $stream->get_trimmed_text("/td");
$comment =~ s/\xa0//g;

# Now go to the end of the block
$stream->get_tag("/td");
$stream->get_tag("/td");
$stream->get_tag("/tr");

# OK, now we have the details, we need to put them into a feed
# Do what you want with the info:


if ($status) {
$rss->add_item( title=>"$status $location $date_text $time_text",
link=>"http://fedex.com/us/tracking/?action=track&tracknumber_list=$tracking_number",
description => "Package number $tracking_number was last seen in $location at $time_text on $date_text, with the status, $status. $comment Godspeed, little parcel! Onward, tiny package!"
);
}

# Stop parsing after the pickup line.
last PARSE if ($status eq "Picked up ");
}

print header('application/rss+xml');
print $rss->as_string;

