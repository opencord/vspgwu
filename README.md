# Virtual Serving/PDN Gateway User plane Service

## Onboarding

To onboard this service in your system, you can add the service to the `mcord.yml` profile manifest:

```
xos_services:
  - name: vspgwu
    path: orchestration/xos_services/vspgwu
    keypair: mcord_rsa
```
