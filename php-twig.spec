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
%global github_version   1.23.0
%global github_commit    5868cd822fd6cf626d5f805439575f9c323cee2a

# Lib
%global composer_vendor  twig
%global composer_project twig

# Ext
%global ext_name twig
%global with_zts 0%{?__ztsphp:1}
%if "%{php_version}" < "5.6"
%global ini_name %{ext_name}.ini
%else
%global ini_name 40-%{ext_name}.ini
%endif

# "php": ">=5.2.7"
%global php_min_ver 5.2.7

# Build using "--without tests" to disable tests
%global with_tests 0%{!?_without_tests:1}

%{!?phpdir:      %global phpdir      %{_datadir}/php}
%{!?php_inidir:  %global php_inidir  %{_sysconfdir}/php.d}

Name:          php-%{composer_project}
Version:       %{github_version}
Release:       2%{?dist}
Summary:       The flexible, fast, and secure template engine for PHP

Group:         Development/Libraries
License:       BSD
URL:           http://twig.sensiolabs.org
Source0:       https://github.com/%{github_owner}/%{github_name}/archive/%{github_commit}/%{name}-%{github_version}-%{github_commit}.tar.gz

# https://github.com/twigphp/Twig/pull/1905 (merged)
Patch0:        %{name}-upstream.patch

BuildRequires: php-devel >= %{php_min_ver}
# Tests
%if %{with_tests}
BuildRequires: %{_bindir}/phpunit
## phpcompatinfo (computed from version 1.22.2)
BuildRequires: php-ctype
BuildRequires: php-date
BuildRequires: php-dom
BuildRequires: php-hash
BuildRequires: php-iconv
BuildRequires: php-json
BuildRequires: php-mbstring
BuildRequires: php-pcre
BuildRequires: php-reflection
BuildRequires: php-spl
%endif

# Lib
## composer.json
Requires:      php(language) >= %{php_min_ver}
## phpcompatinfo (computed from version 1.22.2)
Requires:      php-ctype
Requires:      php-date
Requires:      php-dom
Requires:      php-hash
Requires:      php-iconv
Requires:      php-json
Requires:      php-mbstring
Requires:      php-pcre
Requires:      php-reflection
Requires:      php-spl
# Ext
Requires:      php(zend-abi) = %{php_zend_api}
Requires:      php(api)      = %{php_core_api}

# Lib
## Composer
Provides:      php-composer(%{composer_vendor}/%{composer_project}) = %{version}
## Rename
Obsoletes:     php-twig-Twig < %{version}-%{release}
Provides:      php-twig-Twig = %{version}-%{release}
## PEAR
Provides:      php-pear(pear.twig-project.org/Twig) = %{version}
# Ext
## Rename
Obsoletes:     php-twig-ctwig         < %{version}-%{release}
Provides:      php-twig-ctwig         = %{version}-%{release}
Provides:      php-twig-ctwig%{?_isa} = %{version}-%{release}
## PECL
Provides:      php-pecl(pear.twig-project.org/CTwig)         = %{version}
Provides:      php-pecl(pear.twig-project.org/CTwig)%{?_isa} = %{version}

# This pkg was the only one in this channel so the channel is no longer needed
Obsoletes:     php-channel-twig

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif

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
%setup -qn %{github_name}-%{github_commit}

%patch0 -p1

: Ext -- NTS
mv ext/%{ext_name} ext/NTS
%if %{with_zts}
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
 * Autoloader for %{name} and its' dependencies
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
%if %{with_zts}
pushd ext/ZTS
%{_bindir}/zts-phpize
%configure --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
popd
%endif


%install
: Lib
mkdir -p %{buildroot}%{phpdir}
cp -rp lib/* %{buildroot}%{phpdir}/

: Ext -- NTS
make -C ext/NTS install INSTALL_ROOT=%{buildroot}
install -D -m 0644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}
: Ext -- ZTS
%if %{with_zts}
make -C ext/ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 0644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif


%check
: Library version check
%{_bindir}/php -r 'require_once "%{buildroot}%{phpdir}/Twig/autoload.php";
    exit(version_compare("%{version}", Twig_Environment::VERSION, "=") ? 0 : 1);'

: Extension version check
EXT_VERSION=`grep PHP_TWIG_VERSION ext/NTS/php_twig.h | awk '{print $3}' | sed 's/"//g'` \
    %{_bindir}/php -r 'exit(version_compare("%{version}", getenv("EXT_VERSION"), "=") ? 0 : 1);'

: Extension NTS minimal load test
%{_bindir}/php --no-php-ini \
    --define extension=ext/NTS/modules/%{ext_name}.so \
    --modules | grep %{ext_name}

%if %{with_zts}
: Extension ZTS minimal load test
%{__ztsphp} --no-php-ini \
    --define extension=ext/ZTS/modules/%{ext_name}.so \
    --modules | grep %{ext_name}
%endif

%if %{with_tests}
: Skip tests known to fail
sed -e 's#function testGetAttributeExceptions#function SKIP_testGetAttributeExceptions#' \
    -e 's/function testGetAttributeWithTemplateAsObject/function skip_testGetAttributeWithTemplateAsObject/' \
    -i test/Twig/Tests/TemplateTest.php
%ifarch ppc64
sed 's/function testGetAttributeWithTemplateAsObject/function SKIP_testGetAttributeWithTemplateAsObject/' \
    -i test/Twig/Tests/TemplateTest.php
%endif

: Test suite without extension
%{_bindir}/phpunit --bootstrap %{buildroot}%{phpdir}/Twig/autoload.php --verbose

: Test suite with extension
%{_bindir}/php --define extension=ext/NTS/modules/%{ext_name}.so \
    %{_bindir}/phpunit --bootstrap %{buildroot}%{phpdir}/Twig/autoload.php --verbose
%else
: Tests skipped
%endif


%files
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc CHANGELOG README.rst composer.json
# Lib
%{phpdir}/Twig
# Ext
## NTS
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{ext_name}.so
## ZTS
%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{ext_name}.so
%endif


%changelog
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
