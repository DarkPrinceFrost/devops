# This is a basic VCL configuration file for varnish.  See the vcl(7)
# man page for details on VCL syntax and semantics.
C{
        #include <string.h>
        #include <stdlib.h>
        #include <time.h>

        void TIM_format(double t, char *p);
        double TIM_real(void);
        time_t TIM_parse(const char *p);
}C

acl block {
"XX.XX.XX.XX"; 
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";  # equellaurlbot/1.0 2014-06-03 - dtw
"XX.XX.XX.XX";    # equellaurlbot/1.0 2014-06-04 - dtw
"XX.XX.XX.XX";  # equellaurlbot/1.0 2014-06-04 - dtw
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX"; # lonestar doebile end slash problem - temp
"XX.XX.XX.XX";
"XX.XX.XX.XX";
# added the next 7 on 2014-08-27 - dtw
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
"XX.XX.XX.XX";
# see also user-agent block for equella below
}


# haproxy balancer
backend backend_0 {
.host = "XX.XX.XX.XX";
.port = "8888";
.connect_timeout = 0.4s;
.first_byte_timeout = 1200s;
.between_bytes_timeout = 600s;
}

## mobile
#backend backend_1 {
#.host = "XX.XX.XX.XX";
#.port = "5000";
#.connect_timeout = 0.4s;
#.first_byte_timeout = 600s;
#.between_bytes_timeout = 60s;
#}

# static files
backend backend_2 {
.host = "XX.XX.XX.XX";
.port = "8080";
.connect_timeout = 0.4s;
.first_byte_timeout = 60s;
.between_bytes_timeout = 10s;
}

backend rewrite_webview {
.host = "XX.XX.XX.XX";
.port = "8081";
.connect_timeout = 0.4s;
.first_byte_timeout = 600s;
.between_bytes_timeout = 60s;
}

backend rewrite_resources {
.host = "tundra.example.com";
.port = "8888";
.connect_timeout = 0.4s;
.first_byte_timeout = 600s;
.between_bytes_timeout = 60s;
}

backend rewrite_archive {
.host = "tundra.example.com";
.port = "8888";
.connect_timeout = 0.4s;
.first_byte_timeout = 600s;
.between_bytes_timeout = 60s;
}

acl purge {
    "localhost";
    "XX.XX.XX.XX";
    "XX.XX.XX.XX";
    "XX.XX.XX.XX";
    "XX.XX.XX.XX";
    "XX.XX.XX.XX";
    "XX.XX.XX.XX";
}

acl nocache {
    "XX.XX.XX.XX";
    "XX.XX.XX.XX"/8;
    "XX.XX.XX.XX"/16;
    "XX.XX.XX.XX"/15;
    "XX.XX.XX.XX"/14;
}

import std;

sub vcl_recv {
    if (req.request == "POST" && req.url ~ "^/content/[mc]" && req.url !~ "(reuse_edit|(favorites|lens)_add)_inner" && req.url !~ "@@reuse-edit-view" && req.url !~ "lensAdd" && req.url !~ "setPrintedFile" && req.url !~ "updateParameters" && req.url !~ "manage_addProperty" && req.http.referer !~ "manage_propertiesForm") {
        error 403 "Access denied (POST)";
    }

    if (client.ip ~ block) {
        error 403 "Access denied";
    }

    # cnx rewrite archive
    if (req.http.host ~ "^archive.example.com" || req.url ~ "^/sitemap.xml") {
        set req.backend = rewrite_archive;
        return (lookup);
    }

    # resource images
    if (req.url ~ "^/resources/") {
        set req.backend = rewrite_resources;
        return (lookup);
    }


    if (req.url ~ "^/lenses") {
        if (req.http.user-agent ~ "Baiduspider" 
            || req.http.user-agent ~ "ScoutJet"
            || req.http.user-agent ~ "bingbot") {
            error 403 "Access denied";
        }
    }

    if (req.http.user-agent ~ "equella|360Spider") {
        error 403 "Access denied";
    }

    set req.grace = 120s;
    if (req.http.host ~ "^example.com(:[0-9]+)?$") {

        /* doing the static file dance */
        if (req.url ~ "^/pdfs") {
            set req.backend = backend_2;
            set req.url = regsub(req.url, "^/pdfs", "/files");
        }
        elsif (req.restarts == 0  && req.url ~ "^/content/.*/enqueue$") {
            set req.backend = backend_0;
            return(lookup);
        }
        elsif (req.restarts == 0  && req.url ~ "^/content/(m[0-9]+)/([0-9.]+)/.*format=pdf$") {
            set req.backend = backend_2;
            set req.url = regsub(req.url, "^/content/(m[0-9]+)/([0-9.]+)/.*format=pdf", "/files/\1-\2.pdf");
        }
        elsif (req.restarts == 1  && req.url ~ "^/files/(m[0-9]+)-([0-9.]+)\.pdf") {
            set req.backend = backend_0;
            set req.url = regsub(req.url, "^/files/(m[0-9]+)-([0-9.]+)\.pdf", "/content/\1/\2/?format=pdf");
        }
        elsif (req.url ~ "^/content/((col|m)[0-9]+)/([0-9.]+)/(pdf|epub)$") {
            set req.backend = backend_2;
            set req.url = regsub(req.url, "^/content/((col|m)[0-9]+)/([0-9.]+)/.*(pdf|epub)", "/files/\1-\3.\4");
        }
        elsif (req.url ~ "^/content/((col|m)[0-9]+)/([0-9.]+)/(complete|offline)$") {
            set req.backend = backend_2;
            set req.url = regsub(req.url, "^/content/((col|m)[0-9]+)/([0-9.]+)/(complete|offline)", "/files/\1-\3.\4.zip");
        }
        elsif (req.url ~ "^/content/(col[0-9]+)/([0-9.]+)/source$") {
            set req.backend = backend_2;
            set req.url = regsub(req.url, "^/content/(col[0-9]+)/([0-9.]+)/source", "/files/\1-\2.xml");
        }
        elsif (req.url ~ "^/content/((col|m)[0-9]+)/(([0-9.]+)|latest)/?") {
            set req.backend = rewrite_archive;
        }
        elsif (req.url ~ "^/content/((col|m)[0-9]+)/(([0-9.]+)|latest)/\?collection=col[0-9]*") {
            set req.backend = rewrite_archive;
        }
        // special cases for legacy
        elsif (req.url ~ "^/images/(advice\.png|example\.png|missing\.eps\.metadata|thick-left-arrow\.png|annot\.png|explanation\.png|question\.png|change\.png|magnify-glass-cnx\.png|rhaptos_powered\.png|comment\.png|missing\.eps|seealso\.png)"
               || req.url ~ "^/scripts/(fileSizeUnits|getUser|selectAllNoneInverse)") {
            set req.backend = backend_0;
        }
        elseif ( req.url ~ "^/aboutus/" ) {
            /*  avoid multiple rewrites on restart */
            if (req.url !~ "VirtualHostBase" ) {
                set req.url = "/VirtualHostBase/http/example.com:80/plone/VirtualHostRoot" + req.url;
            }
            set req.backend = backend_0;
        }
        // all rewrite webview
        elsif (req.url ~ "_escaped_fragment_=" || req.url ~ "^/$" || req.url ~ "^/opensearch\.xml" || req.url ~ "^/search" || req.url ~ "^/contents$" || req.url ~ "^/(contents|data|exports|styles|fonts|bower_components|node_modules|images|scripts)/" || req.url ~ "^/(about|about-us|people|contents|donate)") {
            set req.backend = rewrite_webview;
            return(lookup);
        }
        // everything else (including 404)
        else {
            /*  avoid multiple rewrites on restart */
            if (req.url !~ "VirtualHostBase" ) {
                set req.url = "/VirtualHostBase/http/example.com:80/plone/VirtualHostRoot" + req.url;
            }
            set req.backend = backend_0;
        }
    }
    elsif (req.http.host ~ "^passthru") {
        set req.backend = backend_0;
    }
    elsif (req.http.host ~ "^siyavula.example.com") {
        set req.url = "/VirtualHostBase/http/siyavula.example.com:80/plone/VirtualHostRoot" + req.url;
    }
    elsif (req.http.host ~ "^legacy.example.com") {
        /*  avoid multiple rewrites on restart */
        if (req.url !~ "VirtualHostBase" ) {
            set req.url = "/VirtualHostBase/http/legacy.example.com:80/plone/VirtualHostRoot" + req.url;
        }
        set req.backend = backend_0;
    }
	else     {
		error 750 "Moved Permanently" ;
	}
    
    if (req.request == "PURGE") {
        if (!client.ip ~ purge) {
            error 405 client.ip;
        }
        set req.url = req.url + "$";
        ban_url(req.url);
        std.log("purge url: " + req.url);
        error 200 "Purged";
    }
   if (req.request == "PURGE_REGEXP") {
        if (!client.ip ~ purge) {
                error 405 "Not allowed.";
        }
        ban_url(req.url);
        std.log("purge regexp: " + req.url);
        error 200 "Purged";
    }

    if (req.request != "GET" && req.request != "HEAD") {
        /* We only deal with GET and HEAD by default */
        return(pass);
    }

    if (req.http.If-None-Match) {
        return(pass);
    }

    if (req.url ~ "createObject") {
        return(pass);
    }

    if (req.url ~ "//$") {
        error 700 "Bad URL";
    }

    call normalize_accept_encoding;
    call annotate_request;
    return(lookup);
}

sub vcl_pipe {
    # This is not necessary if you do not do any request rewriting.
    set req.http.connection = "close";
}

sub vcl_hit {
    if (obj.ttl <= 0s) {
        return(pass);
    }
    if (req.request == "PURGE") {
        set obj.ttl = 0s;
        error 200 "Purged";
    }
    if (req.http.X-Force-Refresh == "refresh") {
        # Allow client refresh via magic header
        set obj.ttl = 0s;
        return (restart);
    }
    if (req.http.Cache-Control ~ "no-cache") {
        # like msnbot that send no-cache with every request.
        if (client.ip ~ nocache) {
            set obj.ttl = 0s;
            return (restart);
        } 
    }
}

sub vcl_miss {
    if (req.request == "PURGE") {
        error 404 "Not in cache";
    }

}

sub vcl_fetch {
    if (beresp.status >= 500) {
        set beresp.ttl = 0s;
    }
    if (beresp.status == 404 && req.url ~ "^/files/(m[0-9]+)-([0-9.])+\.pdf") {
	return (restart);
    }
    if (beresp.status >= 300) {
        if (req.url !~ "/content/") {
            set beresp.http.X-Varnish-Action = "FETCH (pass - status > 300, not content)";
            return(hit_for_pass);
        }
    }

    set beresp.grace = 120s;
    if (beresp.ttl <= 0s) {
        set beresp.http.X-Varnish-Action = "FETCH (pass - not cacheable)";
        return(hit_for_pass);
    }

    if (!beresp.http.Cache-Control ~ "s-maxage=[1-9]" && beresp.http.Cache-Control ~ "(private|no-cache|no-store)") {
        set beresp.http.X-Varnish-Action = "FETCH (pass - response sets private/no-cache/no-store token)";
        return(hit_for_pass);
    }
    if (req.http.Authorization && !beresp.http.Cache-Control ~ "public") {
        set beresp.http.X-Varnish-Action = "FETCH (pass - authorized and no public cache control)";
        return(hit_for_pass);
    }
    if (req.http.X-Anonymous && !beresp.http.Cache-Control) {
        set beresp.ttl = 600s;
        set beresp.http.X-Varnish-Action = "FETCH (override - backend not setting cache control)";
    }

    if (req.http.host  ~ "^archive.example.com") {
        if (req.url ~ "^/contents/") {
            set beresp.ttl = 3600s;
            set beresp.http.X-Varnish-Action = "FETCH (override - archive contents)";
        }
        if (req.url ~ "^/extras") {
            set beresp.ttl = 600s;
            set beresp.http.X-Varnish-Action = "FETCH (override - archive extras)";
        }
    }
    if (req.url ~ "^/contents/") {
        set beresp.ttl = 7d;
        set beresp.http.X-Varnish-Action = "FETCH (override - archive contents)";
    }

    if (req.url ~ "^/resources") {
        set beresp.ttl = 30d;
        set beresp.http.X-Varnish-Action = "FETCH (override - resources)";
    }

    # Default based on %age of Last-Modified, like squid
    if (!beresp.http.Cache-Control && !beresp.http.Expires && !beresp.http.X-Varnish-Action) {
        C{
            double factor = 0.2;
            double age = 0;
            char *lastmod = 0;
            time_t lmod;
            
            lastmod = VRT_GetHdr(sp, HDR_BERESP, "\016Last-Modified:");
            if (lastmod) {
                lmod =  TIM_parse(lastmod);
                age = TIM_real() - lmod;
                VRT_l_beresp_ttl(sp, age*factor);  
            } 
         }C
        set beresp.http.X-FACTOR-TTL = "ttl: " + beresp.ttl;
    }

    if (req.url ~ "content/OAI\?verb=List(Identifier|Record)s&metadataPrefix=[^&]*$") {
        set beresp.ttl = 7d; 
        set beresp.http.X-My-Header = "OAI";
    }
    if (req.url ~ "content/randomContent") {
        return(hit_for_pass);
    }
    if (req.url ~ "content/[^/]*/[0-9.]*/(\?format=)?pdf$") {
        set beresp.ttl = 7d; 
        set beresp.http.X-My-Header = "VersionedPDF";
    }
    if (req.url ~ "content/[^/]*/latest/(\?format=)?pdf$") {
        set beresp.http.X-My-Header = "LatestPDF";
        return(hit_for_pass);
    }
    if (req.url ~ "content/[^/]*/[0-9.]*/offline$") {
        set beresp.ttl = 90d; 
        set beresp.http.X-My-Header = "VersionedOfflineZip";
    }
    if (req.url ~ "content/[^/]*/[0-9.]*/complete$") {
        set beresp.ttl = 90d; 
        set beresp.http.X-My-Header = "VersionedCompleteZip";
    }
    call rewrite_s_maxage;
    set beresp.http.X-FACTOR-TTL = "ttl: " + beresp.ttl;
    return(deliver);
}

sub vcl_error {
    if (obj.status == 750) {
        set obj.http.Location = "http://" + regsub(req.http.host,"^[^:]*","example.com") + req.url;
        set obj.status = 301;
        return(deliver);
    } elsif (obj.status == 700) {
        set obj.http.Location = req.http.host + regsub(req.url,"//$","/");
        set obj.status = 301;
        return(deliver);
    }
}

sub vcl_deliver {
        if (obj.hits > 0) {
                set resp.http.X-Cache = "HIT";
        } else {
                set resp.http.X-Cache = "MISS";
        }
    call rewrite_age;
}

sub vcl_hash {
    hash_data(req.url);
    if (req.http.host) {
        hash_data(req.http.host);
    } else {
        hash_data(server.ip);
    }
    if (req.http.Accept ~ "application/xhtml\+xml" && req.url ~ "^/contents/") {
        hash_data("application/xhtml+xml");
    }
    return (hash);
}

##########################
#  Helper Subroutines
##########################

# Optimize the Accept-Encoding variant caching
sub normalize_accept_encoding {
    if (req.http.Accept-Encoding) {
        if (req.url ~ "\.(jpe?g|png|gif|swf|pdf|gz|tgz|bz2|tbz|zip)$" || req.url ~ "/image_[^/]*$") {
            remove req.http.Accept-Encoding;
        } elsif (req.http.Accept-Encoding ~ "gzip") {
            set req.http.Accept-Encoding = "gzip";
        } else {
            remove req.http.Accept-Encoding;
        }
    }
}

# Keep auth/anon variants apart if "Vary: X-Anonymous" is in the response
# Also, duplicate logic of content_type_decide, in support of IE8
sub annotate_request {
    # X-Collection
    if (req.http.cookie ~ "(^|.*; )courseURL=") {
        set req.http.X-Collection = regsub(req.http.cookie, "^.*?courseURL=([^;]*);*.*$", "\1");
    }
    if (!(req.http.Authorization || req.http.cookie ~ "(^|.*; )__ac=" || req.http.cookie ~ "(^|.*; )cosign")) {
        set req.http.X-Anonymous = "True";
    }
    if (req.http.Accept ~ "application\/xhtml\+xml") {
        set req.http.X-Content-Type = "application/xhtml+xml";
    } else {
        set req.http.X-Content-Type = "text/html";
    }

}

# The varnish response should always declare itself to be fresh
sub rewrite_age {
    if (resp.http.Age) {
        set resp.http.X-Varnish-Age = resp.http.Age;
        set resp.http.Age = "0";
    }
}

# Rewrite s-maxage to exclude from intermediary proxies
# (to cache *everywhere*, just use 'max-age' token in the response to avoid this override)
sub rewrite_s_maxage {
    if (beresp.http.Cache-Control ~ "s-maxage") {
        set beresp.http.Cache-Control = regsub(beresp.http.Cache-Control, "s-maxage=[0-9]+", "s-maxage=0");
    }
}

