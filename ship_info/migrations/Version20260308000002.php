<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260308000002 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Add UNIQUE KEY (route_id, operation_date) to operations to enable UPSERT';
    }

    public function up(Schema $schema): void
    {
        // 重複行を除去（同一 route_id + operation_date のうち id が最大のものを残す）
        $this->addSql('
            DELETE o1 FROM operations o1
            INNER JOIN operations o2
                ON o1.route_id = o2.route_id
                AND o1.operation_date = o2.operation_date
                AND o1.id < o2.id
        ');

        // UNIQUE KEY を追加
        $this->addSql('ALTER TABLE operations ADD UNIQUE KEY unique_route_date (route_id, operation_date)');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE operations DROP INDEX unique_route_date');
    }
}
