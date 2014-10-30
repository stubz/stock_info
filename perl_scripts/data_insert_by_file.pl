#!/usr/local/bin/perl -w

# read specified csv files and insert stock data 
# into data base stock_db.
# Often, especially after reboot, mysql is not lauched, and
# stock_data_insert.pl fails to insert data. This script is helpful
# when manually insert data into data base by specifying csv files.
#
# use : 
# perl data_insert_by_file.pl file1.csv, file2.csv, ...
# 
use strict;
use lib qw(/Users/popopopo/myWork/perl);
use stock_db; 
use SQL::Abstract;

# my $tbl = "priceDailyRaw";
my $tbl = "priceWeeklyRaw";

if ( @ARGV < 1 ) {
	print "usage : perl data_insert_by_file.pl file1.csv...\n";
	exit;
}

# connect to db
my $dbh = stock_db::connect ();
print "connected to stock_db\n\n";

$dbh->{AutoCommit} = 0; # enable transactions, if possible.
$dbh->{RaiseError} = 1;

foreach my $file (@ARGV){
  &insert_data_db($file);
  print $file," inserted.\n";
}

$dbh->disconnect();
print "disconnected\n";

# sub routine to read one file and insert data
sub insert_data_db()
{
  # get a file name to read which is passed from main routine.
  my $csv_file = shift @_;
  # print $csv_file,"\n";

  # open the file and read each line 
  open FH, "<$csv_file" or die "Cannot read $csv_file : $!";
	eval {
  while (<FH>){
    chomp;
    # my ($date_c, $code_c, $mkt_code1, $start, $high, $low, $close, $amount)=split /\,/;
    my ($date_c, $code_c, $start, $high, $low, $close, $amount, $mkt_code1)=split /\,/;

    # create query sentence
		my $sqla = SQL::Abstract->new();
		my ($sql, @bind) = $sqla->insert(
				$tbl,
				{
					date       => $date_c,
					stockcd  => $code_c,
					marketcd => $mkt_code1,
					open       => $start,
					high       => $high,
					low        => $low,
					close      => $close,
					volume     => $amount,
				}
			);
		my $sth = $dbh->prepare($sql);
		$sth->execute(@bind);
		$sth->finish;

		# my $query = "INSERT INTO orgkabuka (date_c, code_c, mkt_code1, start, high, low, close, amount) VALUES (\'$date_c,\',$code_c,$mkt_code1,$start,$high,$low,$close,$amount);";
 
    # insert into data base using the query above.
    # print "$query\n";  # just to check...
		# 		$dbh->do($query);

  } # end of while loop
	
	$dbh->commit; # commit by transaction
	}; # end of eval
	if ($@) {
		warn "Transaction aborted because $@";
    # now rollback to undo the incomplete changes
    # but do it in an eval{} as it may also fail
   eval { $dbh->rollback };
  }

  close FH;

} # end of sub routine
