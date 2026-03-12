FROM node:20-alpine AS build

RUN apk update && apk upgrade

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies with explicit ajv installation
RUN npm install --legacy-peer-deps && \
    npm install react-scripts@5.0.1 --save-dev --legacy-peer-deps && \
    npm install ajv@8.17.1 ajv-keywords@5.1.0 --save-dev

# Debug check
RUN echo "=== LISTING ALL INSTALLED PACKAGES ===" && \
    npm list --depth=0 && \
    echo "=== CHECKING AJV MODULE ===" && \
    ls -la node_modules/ajv/dist/compile/ || echo "❌ ajv compile folder missing"

# Copy source
COPY . .

# Build
RUN npm run build

FROM nginx:alpine
RUN apk update && apk upgrade
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]