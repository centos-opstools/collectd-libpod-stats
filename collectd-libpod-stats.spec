# Generated by go2rpm 1
%bcond_without check

# https://github.com/pleimer/collectd-libpod-stats
%global goipath         github.com/pleimer/collectd-libpod-stats
Version:                1.0.2

%gometa
%global plugin_name libpodstats
%global collectd_version 5.8.1
%global go_collectd_version v0.5.0

%global common_description %{expand:
Collectd plugin for monitoring resource usage of containers managed by libpod.}

%global golicenses      LICENSE
%global godocs          README.md

Name:           collectd-libpod-stats
Release:        1%{?dist}
Summary:        Collectd plugin for monitoring resource usage of containers managed by libpod

License:        MIT
URL:            %{gourl}
Source0:        %{gosource}
Source1:        https://github.com/collectd/collectd/archive/collectd-%{collectd_version}.tar.gz
Source2:        https://github.com/collectd/go-collectd/archive/%{go_collectd_version}.tar.gz 

BuildRequires:  golang(github.com/pkg/errors)
BuildRequires:  golang(golang.org/x/sys/unix)
BuildRequires:  golang(github.com/google/go-cmp/cmp)
BuildRequires:  golang(go.uber.org/multierr)
BuildRequires:  autoconf
BuildRequires:  automake 
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  libtool
BuildRequires:  pkg-config
BuildRequires:  make
BuildRequires:  gcc

Requires:  collectd

%description
%{common_description}

%gopkg

%prep
%goprep
%setup -T -D -q -a 1 -n %{extractdir}
mkdir %{gobuilddir}/src/collectd.org/
cd %{gobuilddir}/src/collectd.org/
gzip -dc %{SOURCE2} | tar --strip-components=1 -xvvf -

%build
export COLLECTD_SRC="%{_builddir}/%{extractdir}/collectd-collectd-%{collectd_version}"
cd $COLLECTD_SRC
./build.sh

# must run collectd configure for go-collectd dependencies
./configure

CGO_CPPFLAGS="-I${COLLECTD_SRC}/src/daemon -I${COLLECTD_SRC}/src" \
GOPATH="%{gobuilddir}:${GOPATH:+${GOPATH}:}/usr/share/gocode" GO111MODULE=off \
go build -buildmode c-shared -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-}-X github.com/pleimer/collectd-libpod-stats/version=1.0 -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n') -extldflags '-Wl,-z,relro -Wl,--as-needed  -Wl,-z,now -specs=/usr/lib/rpm/redhat/redhat-hardened-ld '" -a -v -x -o %{gobuilddir}/lib/%{plugin_name}.so %{goipath}/plugin/


%install
%gopkginstall
install -m 0755 -vd %{buildroot}%{_libdir}/collectd/ %{buildroot}%{_datadir}/collectd/
install -m 0755 -vp %{gobuilddir}/lib/* %{buildroot}%{_libdir}/collectd/ 
install -m 0644 -vp %{_builddir}/%{extractdir}/types.db.%{plugin_name} %{buildroot}%{_datadir}/collectd/

%if %{with check}
%check
%gocheck
%endif

%files
%license LICENSE
%doc README.md
%{_libdir}/collectd/%{plugin_name}.so
%{_datadir}/collectd/types.db.%{plugin_name}

%gopkgfiles

%changelog
* Tue Jun 16 16:26:54 EDT 2020 pleimer <pfbleimer@gmail.com> - 1.0.1-1
- Initial package


