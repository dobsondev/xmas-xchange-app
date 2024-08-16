# xmas xchange application

This application contains a containerized Python Flask app that will create a Christmas gift exchange and send SMS messages (via Twilio) to the participants notifying them of who they are buying gifts for. This way no one has to be the "keeper of the secrets" and know who got assigned to who, rather it will be a surprise for everyone involved in the gift exchange including the organizer.

The results of the gift exchange will also be uploaded to AWS S3 storage so that if needed you can, as the organizer of the gift exchange, double check who was assigned to who and solve any issues that may arise.

The basic and easiest setup for this application is to run the application on your local machine using Docker and then hook give it a public URL using `ngrok` which can then be used by the participants to recieve the information of who they were assigned.

I found that the participants have to txt to the Twilio number in order to get the information rather than just have the information sent via a script because it will be blocked by most carriers due to being flagged as spam. For whatever reason if the user messages first it seems to work much better.

### Prerequists

- Docker Desktop
- `ngrok`
- AWS S3 Storage (optional)

## Running the application

Running the application locally is as simple as running the following Docker command:

```bash
docker compose up -d
```

This will run the application on port `5050` on your local machine which can then be tunnelled to via `ngrok`.

## Expose the application via `ngrok`

The easiest and quickest way to get this application up and running quickly is to use `ngrok` to connect to your local API via a tunnel. To create the tunnel to this application, simply run this command while the application is running on your local machine:

```bash
ngrok http http://localhost:5050
```

## Connect the Twilo SMS webhook to ngrok

When running the `ngrok` command from above you will be given a public URL that your application is available at. Copy paste this and enter into your "A message comes in" section of the configuration for your Twilio number.

More documentation:
- https://www.twilio.com/docs/usage/webhooks/messaging-webhooks

## Have users message your Twilio number

At this point users should be able to send a SMS message to your Twilio number containing the wording "Christmas" and it will reply with who they were assigned to in the gift exchange.