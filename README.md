# La Crosse view for Home Assistant

## How to use

1. Install Home Assistant

2. Install HACS

3. Install this integration using HACS (add it as a custom repository)

4. Configure the integration

Simply add the following segment to your `configuration.yaml`:

```yaml
sensor:
  - platform: lacrosseview
    username: regulad@regulad.xyz # Your email
    password: mypassword          # Your password
```
