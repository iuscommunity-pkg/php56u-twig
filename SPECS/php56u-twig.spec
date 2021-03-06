# IUS spec file for php56u-twig, forked from
#
#
# Fedora spec file for php-twig
#
# Copyright (c) 2014-2015 Shawn Iwinski <shawn.iwinski@gmail.com>
#                         Remi Collet <remi@fedoraproject.org>
#
# License: MIT
# http://opensource.org/licenses/MIT
#
# Please preserve changelog entries
#

%global github_owner     twigphp
%global github_name      Twig
%global github_version   1.35.3

# Lib
%global composer_vendor  twig
%global composer_project twig

# Ext
%global ext_name twig
%global ini_name 40-%{ext_name}.ini

%global php php56u

%bcond_without zts
%bcond_with tests

Name:          %{php}-%{composer_project}
Version:       %{github_version}
Release:       1.ius%{?dist}
Summary:       The flexible, fast, and secure template engine for PHP

License:       BSD
URL:           http://twig.sensiolabs.org
Source0:       https://github.com/%{github_owner}/%{github_name}/archive/v%{github_version}.tar.gz

BuildRequires: %{php}-devel
# Tests
%if %{with tests}
BuildRequires: %{_bindir}/phpunit
## phpcompatinfo (computed from version 1.22.2)
BuildRequires: %{php}-ctype
BuildRequires: %{php}-date
BuildRequires: %{php}-dom
BuildRequires: %{php}-hash
BuildRequires: %{php}-iconv
BuildRequires: %{php}-json
BuildRequires: %{php}-mbstring
BuildRequires: %{php}-pcre
BuildRequires: %{php}-reflection
BuildRequires: %{php}-spl
%endif

# Lib
## composer.json
Requires:      php(language)
## phpcompatinfo (computed from version 1.22.2)
Requires:      %{php}-ctype
Requires:      %{php}-date
Requires:      %{php}-dom
Requires:      %{php}-hash
Requires:      %{php}-iconv
Requires:      %{php}-json
Requires:      %{php}-mbstring
Requires:      %{php}-pcre
Requires:      %{php}-reflection
Requires:      %{php}-spl
# Ext
Requires:      php(zend-abi) = %{php_zend_api}
Requires:      php(api)      = %{php_core_api}

# Lib
## Composer
Provides:      php-composer(%{composer_vendor}/%{composer_project}) = %{version}
Provides:      %{php}-composer(%{composer_vendor}/%{composer_project}) = %{version}
## Rename
Provides:      php-twig-Twig = %{version}-%{release}
Provides:      %{php}-twig-Twig = %{version}-%{release}
## PEAR
Provides:      php-pear(pear.twig-project.org/Twig) = %{version}
Provides:      %{php}-pear(pear.twig-project.org/Twig) = %{version}
# Ext
## Rename
Provides:      php-twig-ctwig         = %{version}-%{release}
Provides:      php-twig-ctwig%{?_isa} = %{version}-%{release}
Provides:      %{php}-twig-ctwig         = %{version}-%{release}
Provides:      %{php}-twig-ctwig%{?_isa} = %{version}-%{release}
## PECL
Provides:      php-pecl(pear.twig-project.org/CTwig)         = %{version}
Provides:      php-pecl(pear.twig-project.org/CTwig)%{?_isa} = %{version}
Provides:      %{php}-pecl(pear.twig-project.org/CTwig)         = %{version}
Provides:      %{php}-pecl(pear.twig-project.org/CTwig)%{?_isa} = %{version}

# provide and conflict with stock name
Provides:       php-twig = %{version}
Provides:       php-twig%{?_isa} = %{version}
Conflicts:      php-twig < %{version}

%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_provides_in: %filter_provides_in %{php_ztsextdir}/.*\.so$}
%{?filter_setup}


%description
%{summary}.

* Fast: Twig compiles templates down to plain optimized PHP code. The
  overhead compared to regular PHP code was reduced to the very minimum.

* Secure: Twig has a sandbox mode to evaluate untrusted template code. This
  allows Twig to be used as a template language for applications where users
  may modify the template design.

* Flexible: Twig is powered by a flexible lexer and parser. This allows the
  developer to define its own custom tags and filters, and create its own
  DSL.


%prep
%setup -qn %{github_name}-%{github_version}

: Ext -- NTS
mv ext/%{ext_name} ext/NTS
%if %{with zts}
: Ext -- ZTS
cp -pr ext/NTS ext/ZTS
%endif

: Ext -- Create configuration file
cat > %{ini_name} << 'INI'
; Enable %{ext_name} extension module
extension=%{ext_name}.so
INI

: Create lib autoloader
cat <<'AUTOLOAD' | tee lib/Twig/autoload.php
<?php
/**
 * Autoloader for %{name} and its dependencies
 *
 * Created by %{name}-%{version}-%{release}
 */

require_once __DIR__ . '/Autoloader.php';
Twig_Autoloader::register();
AUTOLOAD


%build
: Ext -- NTS
pushd ext/NTS
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}
popd

: Ext -- ZTS
%if %{with zts}
pushd ext/ZTS
%{_bindir}/zts-phpize
%configure --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
popd
%endif


%install
: Lib
mkdir -p %{buildroot}%{_datadir}/php
cp -rp lib/* %{buildroot}%{_datadir}/php/

: Ext -- NTS
make -C ext/NTS install INSTALL_ROOT=%{buildroot}
install -D -m 0644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}
: Ext -- ZTS
%if %{with zts}
make -C ext/ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 0644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif


%check
: Library version check
%{__php} -r 'require_once "%{buildroot}%{_datadir}/php/Twig/autoload.php";
    exit(version_compare("%{version}", Twig_Environment::VERSION, "=") ? 0 : 1);'

: Extension version check
EXT_VERSION=`grep PHP_TWIG_VERSION ext/NTS/php_twig.h | awk '{print $3}' | sed 's/"//g'` \
    %{_bindir}/php -r 'exit(version_compare("%{version}", getenv("EXT_VERSION"), "=") ? 0 : 1);'

: Extension NTS minimal load test
%{__php} --no-php-ini \
    --define extension=ext/NTS/modules/%{ext_name}.so \
    --modules | grep %{ext_name}

%if %{with zts}
: Extension ZTS minimal load test
%{__ztsphp} --no-php-ini \
    --define extension=ext/ZTS/modules/%{ext_name}.so \
    --modules | grep %{ext_name}
%endif

%if %{with tests}
: Skip tests known to fail
sed -e 's#function testGetAttributeExceptions#function SKIP_testGetAttributeExceptions#' \
    -e 's/function testGetAttributeWithTemplateAsObject/function skip_testGetAttributeWithTemplateAsObject/' \
    -i test/Twig/Tests/TemplateTest.php
%ifarch ppc64
sed 's/function testGetAttributeWithTemplateAsObject/function SKIP_testGetAttributeWithTemplateAsObject/' \
    -i test/Twig/Tests/TemplateTest.php
%endif

: Test suite without extension
%{_bindir}/phpunit --bootstrap %{buildroot}%{_datadir}/php/Twig/autoload.php --verbose

: Test suite with extension
%{_bindir}/php --define extension=ext/NTS/modules/%{ext_name}.so \
    %{_bindir}/phpunit --bootstrap %{buildroot}%{_datadir}/php/Twig/autoload.php --verbose
%else
: Tests skipped
%endif


%files
%license LICENSE
%doc CHANGELOG README.rst composer.json
# Lib
%{_datadir}/php/Twig
# Ext
## NTS
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{ext_name}.so
## ZTS
%if %{with zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{ext_name}.so
%endif


%changelog
* Tue Mar 20 2018 Ben Harper <ben.harper@rackspace.com> - 1.35.3-1.ius
- Latest upstream

* Mon Mar 12 2018 Ben Harper <ben.harper@rackspace.com> - 1.35.2-1.ius
- Latest upstream

* Thu Sep 28 2017 Ben Harper <ben.harper@rackspace.com> - 1.35.0-1.ius
- Latest upstream

* Wed Jul 05 2017 Carl George <carl.george@rackspace.com> - 1.34.4-1.ius
- Latest upstream

* Wed Jun 21 2017 Ben Harper <ben.harper@rackspace.com> - 1.34.3-1.ius
- Latest upstream

* Tue Jun 06 2017 Carl George <carl.george@rackspace.com> - 1.34.2-1.ius
- Latest upstream
- Add bconds for zts and tests

* Thu May 04 2017 Ben Harper <ben.harper@rackspace.com> - 1.33.2-1.ius
- Latest upstream

* Wed Apr 19 2017 Ben Harper <ben.harper@rackspace.com> - 1.33.1-1.ius
- Latest upstream

* Wed Mar 22 2017 Ben Harper <ben.harper@rackspace.com> - 1.33.0-1.ius
- Latest upstream

* Mon Feb 27 2017 Ben Harper <ben.harper@rackspace.com> - 1.32.0-1.ius
- Latest upstream

* Wed Jan 18 2017 Ben Harper <ben.harper@rackspace.com> - 1.31.0-1.ius
- Latest upstream

* Wed Jan 04 2017 Ben Harper <ben.harper@rackspace.com> - 1.30.0-1.ius
- Latest upstream

* Wed Dec 14 2016 Ben Harper <ben.harper@rackspace.com> - 1.29.0-1.ius
- Latest upstream

* Wed Nov 30 2016 Ben Harper <ben.harper@rackspace.com> - 1.28.2-1.ius
- Latest upstream

* Tue Nov 08 2016 Ben Harper <ben.harper@rackspace.com> - 1.27.0-1.ius
- Latest upstream

* Wed Oct 05 2016 Ben Harper <ben.harper@rackspace.com> - 1.26.0-1.ius
- Latest upstream

* Thu Sep 22 2016 Ben Harper <ben.harper@rackspace.com> - 1.25.0-1.ius
- Latest upstream

* Fri Sep 02 2016 Carl George <carl.george@rackspace.com> - 1.24.2-1.ius
- Latest upstream

* Mon Jun 13 2016 Carl George <carl.george@rackspace.com> - 1.24.1-1.ius
- Latest upstream

* Tue Jan 05 2016 Carl George <carl.george@rackspace.com> - 1.23.1-1.ius
- Port to IUS from Fedora
- Remove %%php_min_ver because this package is tied to PHP 5.6
- Don't obsolete stock packages
- Disable test suite

* Thu Nov 05 2015 Remi Collet <remi@fedoraproject.org> - 1.23.1-1
- Update to 1.23.0
- drop patch merged upstream

* Mon Nov  2 2015 Remi Collet <remi@fedoraproject.org> - 1.23.0-2
- fix BC break in NodeTestCase, add upstream patch from
  https://github.com/twigphp/Twig/pull/1905

* Fri Oct 30 2015 Remi Collet <remi@fedoraproject.org> - 1.23.0-1
- Update to 1.23.0

* Sun Oct 11 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.22.2-1
- Updated to 1.22.2 (RHBZ #1262655)
- Added lib and ext version checks

* Sat Sep 12 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.21.2-1
- Updated to 1.21.2 (BZ #1256767)

* Wed Aug 12 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.20.0-1
- Updated to 1.20.0 (BZ #1249259)

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.18.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 11 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.18.2-1
- Updated to 1.18.2 (BZ #1183601)
- Added autoloader

* Sun Jan 04 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.16.3-1
- Updated to 1.16.3 (BZ #1178412)

* Sat Nov 01 2014 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.16.2-1
- Updated to 1.16.2 (BZ #1159523)
- GitHub owner changed from "fabpot" to "twigphp"
- Single license for lib and ext

* Mon Aug 25 2014 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.16.0-2
- Removed obsolete and provide of php-twig-CTwig (never imported into Fedora/EPEL)
- Obsolete php-channel-twig
- Removed comment about optional Xdebug in description (does not provide any new feature)
- Always run extension minimal load test

* Tue Jul 29 2014 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.16.0-1
- Initial package
