%define major 1
%define libname %mklibname %{name} %{major}
%define devname %mklibname %{name} -d
%define staticname %mklibname %{name} -d -s

Name:		shaderc
Version:	2022.2
Release:	1
Summary:	A collection of tools, libraries, and tests for Vulkan shader compilation
Group:		System/Libraries
License:	ASL 2.0
URL:		https://github.com/google/shaderc
Source0:	https://github.com/google/shaderc/archive/v%{version}/%{name}-%{version}.tar.gz
# Patch to unbundle 3rd party code and use system libraries
Patch1:		Drop-third-party-code-in-CMakeLists.txt+system_libs.patch

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	glslang-devel >= 10.11.0.0
BuildRequires:	pkgconfig(SPIRV-Tools)
BuildRequires:	python
BuildRequires:	spirv-headers

%description
A collection of tools, libraries and tests for shader compilation.

Shaderc aims to to provide:
 - a command line compiler with GCC- and Clang-like usage, for better
   integration with build systems
 - an API where functionality can be added without breaking existing clients
 - an API supporting standard concurrency patterns across multiple
   operating systems
 - increased functionality such as file #include support

%package -n glslc
Summary:	A command line compiler for GLSL/HLSL to SPIR-V
Group:		Development/Tools

%description -n glslc
A command line compiler for GLSL/HLSL to SPIR-V.

%package -n %{libname}
Summary:	A library for compiling shader strings into SPIR-V
Group:		System/Libraries

%description -n %{libname}
A library for compiling shader strings into SPIR-V.

%package -n %{devname}
Summary:	Development files for libshaderc
Group:		Development/C++
Requires:	%{libname} = %{version}-%{release}

%description -n %{devname}
A library for compiling shader strings into SPIR-V.
Development files for libshaderc.

%package -n %{staticname}
Summary:	A library for compiling shader strings into SPIR-V (static libraries)
Group:		Development/C++

%description -n %{staticname}
A library for compiling shader strings into SPIR-V.
Static libraries for libshaderc.

%prep
%autosetup -p1 -n %{name}-%{version}

#rm -rf third_party

# Stolen from Gentoo
# Create build-version.inc since we want to use our packaged
# SPIRV-Tools and glslang
echo \"shaderc $(grep -m1 -o '^v[[:digit:]]\{4\}\.[[:digit:]]\(-dev\)\? [[:digit:]]\{4\}-[[:digit:]]\{2\}-[[:digit:]]\{2\}$' CHANGES)\" \
        > glslc/src/build-version.inc
#" <--- workaround for vim syntax highlighting bug, ignore
echo \"spirv-tools $(rpm -q --qf '%%{VERSION}' spirv-tools)\" \
        >> glslc/src/build-version.inc
#" <--- workaround for vim syntax highlighting bug, ignore
echo \"glslang 11.0.0 g\" >> glslc/src/build-version.inc
#" <--- workaround for vim syntax highlighting bug, ignore

# Point to correct include
%if 0
#sed -i 's|SPIRV/GlslangToSpv.h|glslang/SPIRV/GlslangToSpv.h|' libshaderc_util/src/compiler.cc
%endif
%cmake \
	-DSHADERC_SKIP_TESTS=ON \
	-DSHADERC_SKIP_EXAMPLES=ON \
	-G Ninja

%build
# We disable the tests because they don't work with our unbundling of 3rd party.
# See https://github.com/google/shaderc/issues/470
%ninja_build -C build

%install
%ninja_install -C build

%files -n glslc
%doc glslc/README.asciidoc
%license LICENSE
%{_bindir}/glslc

%files -n %{libname}
%doc AUTHORS CHANGES CONTRIBUTORS README.md
%license LICENSE
%{_libdir}/lib%{name}_shared.so.1*

%files -n %{devname}
%{_includedir}/%{name}/
%{_libdir}/lib%{name}_shared.so
%{_libdir}/pkgconfig/%{name}.pc

%files -n %{staticname}
%license LICENSE
%{_libdir}/lib%{name}.a
%{_libdir}/lib%{name}_combined.a
%{_libdir}/pkgconfig/%{name}_static.pc
%{_libdir}/pkgconfig/%{name}_combined.pc
