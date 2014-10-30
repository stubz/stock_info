#!/usr/local/bin/perl -w
use strict;
use lib qw(/Users/popopopo/myWork/perl);
use stock_db;
use File::Basename;
use File::Spec;
use Date::Simple;
use SQL::Abstract;

# variables for wget option used mainly in &download_files()
my $URL = "http://www.edatalab.net/kabu/index.htm";
# my $dwd_dir = "/Users/tatata/myWork/stock_info/data";
# my $cur_dir = "/Users/tatata/myWork/stock_info/perl_scripts";
my $dwd_dir = "/Users/popopopo/myWork/stock_info/data";
my $cur_dir = "/Users/popopopo/myWork/stock_info/perl_scripts";

# my $tableHistDaily = "stockPriceHistDaily";
# my $tableHistWeekly = "stockPriceHistWeekly";
my $tableHistDaily = "priceDailyRaw";
my $tableHistWeekly = "priceWeeklyRaw";
my $tableHistDailyOrg = "orgkabuka";
my $tableCalendarDaily = "calendarDaily";
my $tableCalendarWeekly = "calendarWeekly";

# save LZH file names including their absolute path name
# my @dat_files; 
# save LZH file names ( reference to an array )
my ($daily_files_ref, $weekly_files_ref);

# save date of data to be inserted
my @dateList;

# save date in yyyymmdd format
my $date_name;
# log file name
my $log_name;

####################################################################################################
####################################################################################################
####################################################################################################
# -- start of programme -- #

# get date in yyyymmdd format and specify the name of log file
$date_name = get_date();
# set log file name
$log_name = $date_name . "_download.log";

# change current directory
change_directory($cur_dir);

# download files using wget
download_files($log_name, $dwd_dir, $URL);
print "Download finished...\n\n";

# get LZH file names from wget log file
# results are stored in @dat_files
($daily_files_ref, $weekly_files_ref) = get_file_names($log_name);

# connect to db
my $dbh = stock_db::connect ();
print "connected to stock_db\n\n";
$dbh->{AutoCommit} = 0; # enable transactions, if possible.
$dbh->{RaiseError} = 1;

# extract archive files 
# and insert data into db;
if ( @{$daily_files_ref} > 0 ) {
	@dateList = ();
	# daily data
	insert_data_db($daily_files_ref, $cur_dir, $tableHistDaily, $dbh);
	# insert date into calendar table
	insertDateToCalendarTable(\@dateList, $tableCalendarDaily, $dbh);
	# daily data copy
	# insert_data_db($daily_files_ref, $cur_dir, $tableHistDailyOrg, $dbh);

}
if ( @{$weekly_files_ref} > 0 ) {
	@dateList = ();
	# weekly data
	insert_data_db($weekly_files_ref, $cur_dir, $tableHistWeekly, $dbh);
	# insert date into calendar table
	insertDateToCalendarTable(\@dateList, $tableCalendarWeekly, $dbh);
}

# disconnect
$dbh->disconnect();
print "\nDisconnected\n";

####################################################################################################
####################################################################################################
####################################################################################################

# ------ sub routines ------ #
sub get_date
{
	my $date = Date::Simple->new();
	return $date->format('%Y%m%d');
}

sub change_directory
{
	my $dir_name = shift;
  chdir $dir_name or die "cannot chdir to $dir_name : $!";
}

sub download_files
{
  # download stock data into local directory ($dir_download) and save 
  # its log to local file ($log_name). URL is specified by the global variable $URL
  #
  # -t = 5 : 5 attemps only
  # -r     : download recursively
  # -A     : download all files with the specified extension name (.LZH in this case)
  # -nc    : ignore if a file with the same name already exists
  # -nH    : do not save host name in the local file name
  # -o     : specify log file name "dw_today.log" in this case
  # -P     : specify local directory to save downloaded items

	my $file_name = shift;
	my $dir_name = shift;
	my $url_name = shift;
	
	# `/sw/bin/wget --tries=5 -r -A .LZH -nc -nH -o $log_name -P $dwd_dir $URL`;
	`/opt/local/bin/wget --tries=5 -r -A .LZH -nc -nH -o $file_name -P $dir_name $url_name`;
}

sub get_file_names
{
  # get downloaded LZH file names from wget log file
  # and store the names in an array list '@dat_files'.

	my $file_name = shift;
	my (@dailyFiles, @weeklyFiles);

	# open LOG, "< $log_name"
		# or die "Cannot read $log_name: $!";
  open LOG, "<$file_name" or die "Cannot read $file_name: $!";
  
  # retrieve all LZH files except "MNAME.LZH"
  while (<LOG>){
    chomp;
    # downloaded files are save as " => `/Users/tatata/ .../***.LZH' " 
    # in wget log file
		# next unless /\s*(=>)+.*LZH/;
    next unless /^[0-9]+.*LZH/;		# format changed, regex modified accordingly. 2009/05/16
		my $name;
		if ( m/\`+.*LZH\'/ ){
			$name = $&;
			$name =~ s/(\'|\`)//g;
		}
		# my $name =~ s/^\`+.*LZH\'$/$&/;

=pod
    s/(\'|\`)//g; # remove ` and '
    my @fields = split /\//;
    shift @fields; # remove the first element
    my $name = join "/", @fields;
    $name = "/$name";
=cut

		# push (@dat_files, $name) if $name =~ /D[0-9]+/ and $name ne "MNAME.LZH";

		# save daily data file names
    push (@dailyFiles, $name) if $name =~ /D[0-9]+/ and $name ne "MNAME.LZH";
		# save weekly data file names
    push (@weeklyFiles, $name) if $name =~ /W[0-9]+/ and $name ne "MNAME.LZH";
  
    # get daily data file name only ( with file name starting with "D" ) 
    # !! NB !! #
    # In wget log file, each downloaded item appears in a sentence
    # which ends with its file name like "filename.LZH". By split this
    # sentence to get the last word (this is what "pop" command does),
    # we can obtain downloaded file names.
    # This program make use of this feature, thus has to be modified 
    # if the format of log file has changed.
    
    # my $name = pop(@list);
    # push (@dat_files, $name) if $name =~ /^D/ and $name ne "MNAME.LZH"; 
  }
  close LOG;

	# return references to the file name arrays
	return (\@dailyFiles, \@weeklyFiles);
}

sub insert_data_db
{
	my $refToFileNames = shift;		# reference to file names
	my $dirName = shift;
	my $tableName = shift;		# table name to insert data
	my $dbh = shift;
	
  my ($date, $stockCode, $marketCode, $open, $high, $low, $close, $volume);
	my ($csv_file, $query);

	# foreach (@dat_files){
  foreach my $fileName (@{$refToFileNames}){
  	# LZH file to extract
  	next unless ( -s $fileName );
		# `/sw/bin/lha egv $fileName`;
  	`/opt/local/bin/lha egv $fileName`;

  	# csv file extracted from LZH
  	$fileName =~ s/.LZH/.csv/i;

  	# truncate file name : extracted files are stored in the current 
  	# directory ( lha cannot specify the extract directory
  	# Filebase :: 
  	# my $csv_file = basename $_;
  	$csv_file = File::Spec->catfile($dirName, basename $fileName);
  
  	open FH, "< $csv_file" or die "Cannot read $csv_file : $!";
		eval{
  	while (<FH>){
    	chomp;
    	($date, $stockCode, $marketCode, $open, $high, $low, $close, $volume) = split /\,/; 

			# insert into table
			my $sqla = SQL::Abstract->new();
			my ($sql, @bind) = $sqla->insert(
				$tableName,
				{
					date     => $date,
					stockcd  => $stockCode,
					marketcd => $marketCode,
					open     => $open,
					high     => $high,
					low      => $low,
					close    => $close,
					volume   => $volume,
				}
			);
			my $sth = $dbh->prepare($sql);
			$sth->execute(@bind);
			$sth->finish;

			# $query = sprintf("INSERT INTO %s (date,stockCode,marketCode,open,high,low,close,volume) VALUES (\'%s\', %s, %s, %s, %s, %s, %s, %s);", $tableName, $date, $stockCode, $marketCode, $open, $high, $low, $close, $volume);

			# execute query
		# $dbh->do($query);

  	} # end of while loop 

		$dbh->commit; 
		}; # end of eval
    if ($@) {
    	warn "Transaction aborted because $@";
    	# now rollback to undo the incomplete changes
    	# but do it in an eval{} as it may also fail
    	eval { $dbh->rollback };
    }

  	close FH;

  	unlink $csv_file;
  	print basename $csv_file;
  	print " inserted.\n";

		push (@dateList, $date);

  } # end of foreach loop

} # end of sub routine insert_data_db

sub insertDateToCalendarTable{
	my $refToDateList = shift;
	my $tableName = shift;		# table name to insert data
	my $dbh = shift;

	my $sqla = SQL::Abstract->new();

	eval{
	foreach my $datename ( @{$refToDateList} ) {
		my ($sql, @bind) = $sqla->insert(
				$tableName,
				{
					date => $datename,
				}
			);
		my $sth = $dbh->prepare($sql);
		$sth->execute(@bind);
		$sth->finish;
	}
	$dbh->commit;
	}; # end of eval
	if ($@){
		warn "Transaction aborted because $@";
		# now rollback to undo the incomplete changes
   	# but do it in an eval{} as it may also fail
   	eval { $dbh->rollback };
  }
}
