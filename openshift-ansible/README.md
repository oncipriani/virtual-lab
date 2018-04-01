# OpenShift 3.7 Installation Known Issues

This document describes known issues and steps that must be followed for a successful [OpenShift Origin](https://docs.openshift.org/latest/welcome/index.html) installation.

In short, the following steps must be taken to successfully deploy OpenShift with Ceph Storage, starting from scratch:

1. Follow the [Host Preparation](https://docs.openshift.com/container-platform/3.7/install_config/install/host_preparation.html) instructions;

1. Install required packages on the control host (the host running Ansible):
   - python-passlib;
   - apache2-utils (provides `htpasswd`);
   - java-1\_8\_0-openjdk-headless (provides `keytool`).

1. Perform an [Advanced Installation](https://docs.openshift.com/container-platform/3.7/install_config/install/advanced_install.html) of OpenShift **without** persistent storage for *logging* and *metrics* (or do not deploy them);

1. Configure OpenShift to [use Ceph RBD for Dynamic Provisioning](https://docs.openshift.com/container-platform/3.7/install_config/storage_examples/ceph_rbd_dynamic_example.html);

1. (Re)deploy *logging* and *metrics*.

## Logging and Metrics must be deployed after the initial install

Logging, Registry and Metrics should use persistent storage on production clusters. NFS should **not** be used for production, since it has known issues:

- Image Push Errors with Scaled Registry Using Shared NFS Volume;
  - https://docs.openshift.com/container-platform/3.7/install_config/registry/registry_known_issues.html#known-issue-nfs-image-push-fails
- OpenShift metrics uses the Cassandra database as a datastore for metrics. However, using network storage in combination with Cassandra is not recommended;
  - https://docs.openshift.com/container-platform/3.7/install_config/cluster_metrics.html#metrics-persistent-storage
- Using NFS storage as a volume or a persistent volume (or via NAS such as Gluster) is not supported for Elasticsearch storage, as Lucene relies on file system behavior that NFS does not supply.
  - https://docs.openshift.com/container-platform/3.7/install_config/aggregate_logging.html#aggregated-elasticsearch

However, in order to use other kinds of persistent storages for *metrics* and *logging*, the OpenShift Cluster must be running. So, an initial installation without these components must first be successfully completed.

## Ceph Storage Cluster must use HAMMER tunables profile

If the Ceph Storage Cluster uses a [tunables profile](http://docs.ceph.com/docs/master/rados/operations/crush-map/#tunables) higher than HAMMER, OpenShift running on CentOS 7.3 will not be able to connect to it.

To set Ceph Storage Cluster tunables profile to HAMMER:
```
# ceph osd crush tunables hammer
```

See https://access.redhat.com/solutions/2591751.

## RBD Kernel module does not support `exclusive-lock`, `object-map`, `fast-diff` and `deep-flatten`

Trying to map a RBD image that has `exclusive-lock`, `object-map`, `fast-diff` or `deep-flatten` features enabled will fail with the following error:
```
rbd: sysfs write failed
rbd: map failed: (6) No such device or address
```

In addition to not being able to map the image, OpenShift will also not be able to bind the image to a Persistent Volume (PV).

In order to be able to map the image or to enable it to be used as an OpenShift PV, disable those features:
```
# rbd feature disable <image> exclusive-lock,object-map,fast-diff,deep-flatten
```

## OpenShift CLI "oc" must be configured on the master nodes

Ansible installation will fail when deploying *logging* if `oc` is not configured to login automatically to the master node as an user that has **system:admin** privileges.

Ensure that the following command executes without errors on the master nodes before proceeding with the OpenShift *logging* or *metrics* deployment:
```
# oc get all --all-namespaces=true
```

## Every project requiring access to Ceph RBD must know the Ceph Secret

When [using Ceph RBD](https://docs.openshift.com/container-platform/3.7/install_config/storage_examples/ceph_rbd_dynamic_example.html), every project that requires access to the Ceph Storage Cluster must know the key allowing access to the cluster.

To make the persistent storage available to every project, you must modify the default project template. Read more on [modifying the default project template](https://docs.openshift.com/container-platform/3.7/admin_guide/managing_projects.html#selfprovisioning-projects). Adding this to your default project template allows every user who has access to create a project access to the Ceph cluster.

## Other minor issues

The following message appears on all nodes after installing OpenShift:
```
Failed to read directory /usr/share/oci-umount/oci-umount.d: No such file or directory
```

Manually creating the missing directory `mkdir -p /usr/share/oci-umount/oci-umount.d` on all Red Hat OpenShift Container Platform nodes will workaround the problem.

See Red Hat [KB 3291271](https://access.redhat.com/solutions/3291271).
