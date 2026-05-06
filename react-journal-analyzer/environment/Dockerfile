FROM node:20-bookworm@sha256:8f693eaa7e0a8e71560c9a82b55fd54c2ae920a2ba5d2cde28bac7d1c01c9ba5

RUN mkdir -p /app/vendor && \
    curl -sLo /app/vendor/react.js https://unpkg.com/react@18.3.1/umd/react.production.min.js && \
    curl -sLo /app/vendor/react-dom.js https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js && \
    curl -sLo /app/vendor/babel.js https://unpkg.com/@babel/standalone/babel.min.js && \
    curl -sLo /app/vendor/pdf.js https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js && \
    curl -sLo /app/vendor/pdf.worker.js https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js

WORKDIR /app
