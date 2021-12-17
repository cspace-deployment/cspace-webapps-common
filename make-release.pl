#!/usr/bin/perl
#
# make a release candidate (moderately generic helper form making release tags)

use strict;

if (scalar @ARGV < 3)  {
  print "make a release candidate (moderately generic helper form making release tags)\n";
  print "\n";
  print "./make-release.pl <release> <directory> \"commit comment\" --[new|release])\n";
  print "e.g.\n";
  print "./make-release.pl 5.1.0 radiance \"\" --release\n";
  print "./make-release.pl 5.1.0 radiance \"a few fixes and enhancements\"\n";
  print "\n";
  print "will look in the existing release candidates (if any) for <release> and make the next one in the series\n";
  print "e.g. if the current release candidate is 5.1.0-rc3, this script will make 5.1.0-rc4\n";
  print "\n";
  print "nb: if the release does not exist, you must specify either --release or --new.\n";
  print "    e.g. 5.1.1 does not exist 5.1.1-rc1 is created.\n";
  print "    to make the actual final release tag (e.g. 5.1.1) add --release\n";
  print "    to make a new first release candidate (e.g. 5.1.2-rc1) add --new\n";

  die "Need three (or four arguments): release directory \"comment (can be empty)\" [--new/release]\n";
}

my ($RELEASE, $DIRECTORY, $MSG, $NEW) = @ARGV;

chdir $DIRECTORY or die("could not change to $DIRECTORY directory");
    
my @tags = `git tag --list ${RELEASE}*`;
if ($#tags < 0 && $NEW ne '--new' & $NEW ne '--release') {
   print "can't find any tags for ${RELEASE}\n";
   print "add --new if you want to make a new -rc1 for ${RELEASE}\n";
   print "add --release if you want to make a (release) tag for ${RELEASE}\n";
   exit(1);
}

my ($rc, $highest_rc, $release_to_check, $version_number);

foreach my $tag (sort (@tags)) {
    chomp $tag;
    # print "checking $tag for $RELEASE\n";
    if ($tag eq $RELEASE) {
        $release_to_check = $tag;
        $rc = '';
        last;
    }
    ($release_to_check, $rc) = $tag =~ /^(.*?)\-rc(\d+)/;
    if ($release_to_check eq $RELEASE) {
        $version_number = $release_to_check;
        if (int($rc) > int($highest_rc)) {
            $highest_rc = $rc;
        }
    }
}

print "found version: $release_to_check rc: $highest_rc\n";

if ($release_to_check) {
    if ($NEW eq '--new' && $rc ne '') {
        print "release candidates of version $release_to_check already exist and $NEW was specified\n";
        print "can't make a new '-rc1' with this value.\n";
        print "specify a different version number or don't use $NEW to make a RC.\n";
        exit;
    }
    elsif ($NEW eq '--release' && $rc eq '') {
        print "version $release_to_check already exists and $NEW was specified\n";
        print "can't make a new release with this value.\n";
        print "specify a different version number or don't use $NEW to make a RC.\n";
        exit;
    }
    elsif ($rc eq '') {
        print "an existing release was found for $RELEASE; can't make it again!\n";
        exit;
    }
    if (0) {
        print "and neither --new nor --release were specified\n";
        print "if you want to make this the 1st release candidate for a new release, specify:\n";
        print "$0 some-other-version-number $DIRECTORY \"$MSG\" --new\n";
        print "if you want to make a new release, specify:\n";
        print "$0 some-other-version-number $DIRECTORY \"$MSG\" --release\n";
        exit;
    }
}

if ($NEW eq '--release') {
    print "making release tag for $RELEASE\n";
    $version_number = $RELEASE;
}
else {
    $highest_rc++;
    if ($highest_rc == 1) {print "making a new 1st release candidate for $RELEASE\n"};
    $version_number = "$RELEASE-rc$highest_rc";
}

my $tag_message = "Release tag $version_number.";
$tag_message .= ' ' . $MSG if $MSG;

print "verifying code is current and using main branch...\n";
system "git checkout main";
system "git pull -v";
print "updating CHANGELOG.txt...\n";
system "echo 'CHANGELOG for $DIRECTORY' > CHANGELOG.txt";
system "echo  >> CHANGELOG.txt";
system "echo 'OK, it is not a *real* change log, but a list of changes resulting from git log' >> CHANGELOG.txt";
system "echo 'sometimes with some human annotation after the fact.' >> CHANGELOG.txt";
system "echo  >> CHANGELOG.txt";
system "echo 'This is version $version_number' >> CHANGELOG.txt";
system "echo '$version_number' > VERSION";
system "date >> CHANGELOG.txt ; echo >> CHANGELOG.txt";
system "git log --oneline --decorate >> CHANGELOG.txt";
system "git add CHANGELOG.txt";
system "git commit -m 'revise CHANGELOG.txt and bump version to $version_number'";
system "git push -v" ;
print  "git tag -a $version_number -m '$tag_message'\n";
system "git tag -a $version_number -m '$tag_message'";
system "git push --tags";
