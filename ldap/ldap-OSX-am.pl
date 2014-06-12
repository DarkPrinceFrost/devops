# Stefanus Du Toit, 2005, sjdutoit@cgl.uwaterloo.ca

use Net::LDAP;
use URI;

my $tmpfile = "/tmp/ldapmountmap.$$";
my $mountsfile = "./ldapmountmap";

my $ldap = Net::LDAP->new('ldaps://barracks.cnx.rice.edu/') or die "$@";

$ldap->bind;

my $mesg = $ldap->search(base => 'ou=auto.homes,dc=connexions',
                         filter => '(objectClass=automount)');

$mesg->code && die $mesg->error;

open MOUNTMAP, ">$tmpfile";

foreach $entry ($mesg->all_entries) {
    my $mountpoint = $entry->get_value('cn');
    my $location = $entry->get_value('automountInformation');

    my $uri = URI->new($location);

    my $mesg = $ldap->search(base => $uri->dn,
                             filter => $uri->filter);

    $mesg->code && die $mesg->error;

    MOUNT: foreach $mount ($mesg->all_entries) {
        my $subdir = $mount->get_value('cn');
        my $subloc = $mount->get_value('automountInformation');
        next MOUNT if $subdir eq "";
        $subloc =~ s/&/$subdir/g;
        print MOUNTMAP "$mountpoint/$subdir $subloc\n";
    }
}

close MOUNTMAP;

$ldap->unbind;

# Update the actual mounts file
rename $tmpfile, $mountsfile or die $@;
# Reload the automounter
#system("killall -HUP automount");
