%{!?__pecl:   %{expand: %%global __pecl     %{_bindir}/pecl}}
%global pecl_name mysqlnd_ms

Summary:      A replication and load balancing plugin for mysqlnd
Name:         php-pecl-mysqlnd-ms
Version:      1.1.1
Release:      2%{?dist}

License:      PHP
Group:        Development/Languages
URL:          http://pecl.php.net/package/mysqlnd_ms

Source0:      http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

# From http://www.php.net/manual/en/mysqlnd-ms.configuration.php
Source1:      %{pecl_name}.ini

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: php-devel >= 5.3.6
BuildRequires: php-mysqlnd
BuildRequires: php-pear

Requires(post): %{__pecl}
Requires(postun): %{__pecl}

Requires:     php-mysqlnd%{?_isa}
Requires:     php(zend-abi) = %{php_zend_api}
Requires:     php(api) = %{php_core_api}

Provides:     php-pecl(%{pecl_name}) = %{version}-%{release}
Provides:     php-pecl(%{pecl_name})%{?_isa} = %{version}-%{release}


# RPM 4.8
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_setup}
# RPM 4.9
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$


%description
The replication and load balancing plugin is a plugin for the mysqlnd library.
It can be used with PHP MySQL extensions (ext/mysql, ext/mysqli, PDO_MySQL),
if they are compiled to use mysqlnd. The plugin inspects queries to do
read-write splitting. Read-only queries are send to configured MySQL
replication slave servers all other queries are redirected to the MySQL
replication master server. Very little, if any, application changes required,
dependent on the usage scenario required.

Documentation : http://www.php.net/mysqlnd_ms


%prep 
%setup -c -q

cp %{SOURCE1} %{pecl_name}.ini

cp -r %{pecl_name}-%{version} %{pecl_name}-%{version}-zts


%build
cd %{pecl_name}-%{version}
%{php_bindir}/phpize

# Don't use --enable-mysqlnd-ms-table-filter
# See # http://pecl.php.net/bugs/bug.php?id=24391
%configure \
    --with-libdir=%{_lib} \
    --enable-mysqlnd-ms \
    --with-php-config=%{php_bindir}/php-config
make %{?_smp_mflags}

cd ../%{pecl_name}-%{version}-zts
%{php_ztsbindir}/phpize

%configure \
    --with-libdir=%{_lib} \
    --enable-mysqlnd-ms \
    --with-php-config=%{php_ztsbindir}/php-config
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install -C %{pecl_name}-%{version}     INSTALL_ROOT=%{buildroot}
make install -C %{pecl_name}-%{version}-zts INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
install -D -m 644 %{pecl_name}.ini %{buildroot}%{php_inidir}/%{pecl_name}.ini
install -D -m 644 %{pecl_name}.ini %{buildroot}%{php_ztsinidir}/%{pecl_name}.ini

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml


%clean
rm -rf %{buildroot}


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%check
cd %{pecl_name}-%{version}
ln -sf %{php_extdir}/mysqlnd.so modules/
ln -sf %{php_extdir}/json.so modules/

# only check if build extension can be loaded
%{__php} -n -q \
    -d extension_dir=modules \
    -d extension=json.so \
    -d extension=mysqlnd.so \
    -d extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}


%files
%defattr(-, root, root, -)
%doc %{pecl_name}-%{version}/{CHANGES,CREDITS,LICENSE,README}
%config(noreplace) %{php_inidir}/%{pecl_name}.ini
%config(noreplace) %{php_ztsinidir}/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so
%{php_ztsextdir}/%{pecl_name}.so
%{pecl_xmldir}/%{name}.xml


%changelog
* Fri Oct 14 2011 Remi Collet <remi@fedoraproject.org> - 1.1.1-2
- update to 1.1.1

* Sun Oct 02 2011 Remi Collet <remi@fedoraproject.org> - 1.1.0-2
- build zts extension

* Sun Oct 02 2011 Remi Collet <remi@fedoraproject.org> - 1.1.0-1
- Initial RPM
