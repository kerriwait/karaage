# -*- coding: utf-8 -*-
#
# Copyright 2007-2014 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

import importlib
from karaage.plugins import BasePlugin


def add_plugin(namespace, plugin_name, django_apps, depends):

    module_name, descriptor_name = plugin_name.rsplit(".", 1)
    module = importlib.import_module(module_name)
    descriptor = getattr(module, descriptor_name)
    assert issubclass(descriptor, BasePlugin)

    value = descriptor.depends
    depends.extend(value)

    value = descriptor.module
    assert value is not None
    django_apps.append(value)

    value = descriptor.django_apps
    django_apps.extend(value)

    value = descriptor.xmlrpc_methods
    namespace.XMLRPC_METHODS += value

    for key, value in descriptor.settings.items():
        try:
            getattr(namespace, key)
            raise RuntimeError(
                'setting %s already exists error adding %s'
                % (key, plugin_name))
        except AttributeError:
            pass

        setattr(namespace, key, value)


def load_plugins(namespace, plugins):
    done = set()
    django_apps = []

    depends = plugins
    while len(depends) > 0:
        new_depends = []
        for plugin in depends:
            if plugin not in done:
                add_plugin(namespace, plugin, django_apps, new_depends)
                done.add(plugin)
        depends = new_depends

    installed_apps = []
    done = set()

    for app in namespace.KARAAGE_APPS:
        if app not in done:
            installed_apps.append(app)
            done.add(app)

    for app in django_apps:
        if app not in done:
            installed_apps.append(app)
            done.add(app)

    for app in namespace.INSTALLED_APPS:
        if app not in done:
            installed_apps.append(app)
            done.add(app)

    namespace.INSTALLED_APPS = installed_apps

    del namespace.KARAAGE_APPS


def post_process(namespace):
    load_plugins(namespace, namespace.PLUGINS)
