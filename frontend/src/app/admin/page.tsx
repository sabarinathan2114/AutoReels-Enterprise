import { AdminConsoleView } from "@/components/admin/AdminConsoleView";

export const metadata = {
  title: "Super Admin Control Plane | AutoReels Enterprise",
  description: "High-privilege administration console for AutoReels Enterprise generation farm and tenant matrix."
};

export default function AdminPage() {
  return <AdminConsoleView />;
}
