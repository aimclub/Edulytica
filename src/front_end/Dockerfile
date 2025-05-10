FROM node:20-alpine

WORKDIR /app

COPY . .

RUN rm -rf node_modules package-lock.json \
    && npm install --legacy-peer-deps --save-dev \
    && chmod +x node_modules/.bin/react-scripts

EXPOSE 3000

CMD ["npm", "start"]
