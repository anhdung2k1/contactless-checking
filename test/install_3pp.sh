HELM_URL="https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3"
KUBECTL_LATEST_VERSION=$(curl -L -s https://dl.k8s.io/release/stable.txt)
echo $KUBECTL_LATEST_VERSION
KUBECTL_URL="https://dl.k8s.io/release/${KUBECTL_LATEST_VERSION}/bin/linux/amd64/kubectl"
KUBECTL_CHECKSUM_URL="https://dl.k8s.io/release/${KUBECTL_LATEST_VERSION}/bin/linux/amd64/kubectl.sha256"

echo "Install 3PP packages"
echo "Install Helm package"
curl -fsSL -o get_helm.sh $HELM_URL
chmod 700 get_helm.sh
./get_helm.sh
rm -f get_helm.sh
echo "Done"
echo "Install Kubectl package"
#Download kubectl binary
curl -LO $KUBECTL_URL
chmod +x kubectl
sudo install -o root -g root -m 0755 kubectl /usr/bin/kubectl
rm -f kubectl
echo "Done"