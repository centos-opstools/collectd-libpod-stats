%bcond_without check

# https://github.com/infrawatch/collectd-libpod-stats
%global goipath         github.com/infrawatch/collectd-libpod-stats

%global provider        github
%global provider_tld    com
%global project         infrawatch
%global repo            collectd-libpod-stats
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     github.com/infrawatch/collectd-libpod-stats
%global shortcommit     %(c=%{commit}; echo ${c:0:7})


Version:                1.0.5

%global plugin_name libpodstats
%global collectd_version 5.11.0
%global go_collectd_version v0.5.0

%global common_description %{expand:
Collectd plugin for monitoring resource usage of containers managed by libpod.}

%global golicenses      LICENSE
%global godocs          README.md

Name:           collectd-libpod-stats
Release:        2%{?dist}
Summary:        Collectd plugin for monitoring resource usage of containers managed by libpod

License:        MIT
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/v%{version}.tar.gz#/%{repo}-%{version}.tar.gz
Source1:        https://github.com/collectd/collectd/archive/collectd-%{collectd_version}.tar.gz
Source2:        https://github.com/collectd/go-collectd/archive/%{go_collectd_version}.tar.gz

BuildRequires:  golang(github.com/pkg/errors)
BuildRequires:  golang(golang.org/x/sys/unix)
BuildRequires:  golang-github-google-cmp
BuildRequires:  golang-uber-multierr
BuildRequires:  golang-uber-atomic
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  libtool
BuildRequires:  pkg-config
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  golang

Requires:  collectd

%description
%{common_description}

%gopkg

%global debug_package %{nil}

%prep
%setup -q -n %{repo}-%{version}
# %setup -T -D -q -a 1 -n %{extractdir}
%global gobuilddir $(pwd)

mkdir -p %{gobuilddir}/src/github.com/infrawatch/collectd-libpod-stats
pushd %{gobuilddir}/src/github.com/infrawatch/collectd-libpod-stats
gzip -dc %{SOURCE0} | tar --strip-components=1 -xvvf -
popd
mkdir -p %{gobuilddir}/src/collectd.org/
pushd %{gobuilddir}/src/collectd.org/
gzip -dc %{SOURCE1} | tar --strip-components=1 -xvvf -
gzip -dc %{SOURCE2} | tar --strip-components=1 -xvvf -

%build
pushd %{gobuilddir}/src/collectd.org/
./build.sh

# must run collectd configure for go-collectd dependencies
./configure
popd
CGO_CFLAGS="-I%{gobuilddir}/src/collectd.org/src/daemon -I%{gobuilddir}/src/collectd.org/src %{build_cflags}" \
GOPATH="%{gobuilddir}:${GOPATH:+${GOPATH}:}/usr/share/gocode" GO111MODULE=off \
go build -buildmode c-shared -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-}-X github.com/infrawatch/collectd-libpod-stats/version=%{Version} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n') -extldflags '%{build_ldflags}'" -a -v -x -o %{gobuilddir}/lib/%{plugin_name}.so %{goipath}/plugin/


%install
install -m 0755 -vd %{buildroot}%{_libdir}/collectd/ %{buildroot}%{_datadir}/collectd/
install -m 0755 -vp %{gobuilddir}/lib/* %{buildroot}%{_libdir}/collectd/
install -m 0644 -vp types.db.%{plugin_name} %{buildroot}%{_datadir}/collectd/

%if %{with check}
%check
# %gocheck
%endif

%files
%license LICENSE
%doc README.md
%{_libdir}/collectd/%{plugin_name}.so
%{_datadir}/collectd/types.db.%{plugin_name}


%changelog
* Wed Apr 19 2023 Matthias Runge <mrunge@redhat.com> - 1.0.5-1
- include records from volatile containers (rhbz#2179071)

* Thu Feb 03 2022 Matthias Runge <mrunge@redhat.com> - 1.0.4-2
- bump release to trigger builds on c8s and c9s

* Tue Oct 12 2021 Paul Leimer <pleimer@redhat.com> - 1.0.4
- move root repository to github.com/infrawatch org
- 391d6bb Account for counter rollover

* Wed Mar 17 2021 Paul Leimer <pleimer@redhat.com> - 1.0.3
- 6174045 remove unused
- 8f9bc8d experimenting on getting collectd global hostname

* Tue Aug 11 2020 Paul Leimer <pleimer@redhat.com> - 1.0.2
- 9a7dcdb Ignore non-existant cgroups
- 6f573e5 Update README.md
- 94e18b3 Ignore non-existant cgroups
- 04c96df fix path generation for all cgroups and users

* Tue Jun 16 16:26:54 EDT 2020 pleimer <pfbleimer@gmail.com> - 1.0.1-1
- Initial package
